import uuid
import sqlalchemy
import database
import models
import datetime
from flask import Flask, request
from celery_worker import task

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello there! It's an exchanger!"


@app.get('/currency')
def all_currency():
    database.init_db()
    date_now = datetime.datetime.now().strftime("%d-%m-%Y")
    all_currency_info = models.Currency.query.filter_by(date=date_now).all()
    return [itm.to_dict() for itm in all_currency_info]


@app.get('/currency/<currency_name>')
def currency(currency_name):
    database.init_db()
    date_now = datetime.datetime.now().strftime("%d-%m-%Y")
    currency_info = models.Currency.query.filter_by(currency_name=currency_name, date=date_now).all()
    return [itm.to_dict() for itm in currency_info]


@app.get('/currency/<currency_name1>/to/<currency_name2>')
def currency_to_currency(currency_name1, currency_name2):
    database.init_db()
    date_now = datetime.datetime.now().strftime("%d-%m-%Y")

    currency_1 = models.Currency.query.filter_by(currency_name=currency_name1, date=date_now).first().buy
    currency_2 = models.Currency.query.filter_by(currency_name=currency_name2, date=date_now).first().sale

    result_exchange = currency_1 / currency_2

    return [{"result": '{:.2f}'.format(result_exchange)}]


@app.post('/currency/<currency_name1>/to/<currency_name2>')
def post_currency_to_currency(currency_name1: str, currency_name2: str):
    user_id = request.get_json()["user_id"]
    amount_to = request.get_json()["amount"]

    database.init_db()
    transaction_id = str(uuid.uuid4())
    date_now = datetime.datetime.now().strftime("%d-%m-%Y")
    transaction = models.Transactions(user_id=user_id, currency_from=currency_name1, currency_to=currency_name2,
                                      amount_spent=amount_to, received_amount=0, rate=0,
                                      commission=0, date=date_now, status="in_processing",
                                      transaction_id=transaction_id)
    database.db_session.add(transaction)
    database.db_session.commit()

    task_obj = task.apply_async(args=[user_id, amount_to, currency_name1, currency_name2, transaction_id])
    return {'task_id': str(task_obj)}


@app.get('/user/<user_id>')
def user_info(user_id):
    database.init_db()
    info = models.Account.query.filter_by(user_id=user_id).all()
    return [itm.to_dict() for itm in info]


@app.get('/user/<user_id>/history')
def user_history(user_id):
    database.init_db()
    history = models.Transactions.query.filter_by(user_id=user_id).order_by(models.Transactions.date.desc()).all()
    return [itm.to_dict() for itm in history]


@app.get('/currency/<currency_name>/rating')
def get_currency_rating(currency_name):
    database.init_db()
    all_ratings = models.Rating.query.filter_by(currency_name=currency_name).all()

    avr_rating = dict(database.db_session.query(sqlalchemy.func.avg(models.Rating.rating).label('Rating')).filter(
        models.Rating.currency_name == currency_name).first())['Rating']

    return {"currency name": currency_name, "average": avr_rating, "all_rating": [i.to_dict() for i in all_ratings]}


@app.route('/currency/<currency_name>/rating', methods=['POST', 'PUT', 'DELETE'])
def currency_rating(currency_name):
    database.init_db()
    request_data = request.get_json()
    user_id = request_data['UserId']
    comment = request_data['Comment']
    rating = request_data['Rating']
    date_now = datetime.datetime.now().strftime("%d-%m-%Y")

    """users all comment/rating to the specified currency"""
    user_rating = models.Rating.query.filter_by(user_id=user_id, currency_name=currency_name).first()

    if request.method == "DELETE":
        database.db_session.delete(user_rating)
        database.db_session.commit()
        return "The rating and comment are deleted."

    elif request.method == "POST":
        new_rating = models.Rating(user_id=user_id, currency_name=currency_name, rating=rating, comment=comment,
                                   date=date_now)
        database.db_session.add(new_rating)
        database.db_session.commit()
        return "The rating and comment are added."

    elif request.method == "PUT":
        models.Rating.query.filter_by(user_id=user_id, currency_name=currency_name).update(
            dict(rating=rating, comment=comment, date=date_now))
        database.db_session.commit()
        return "The rating and comment are edited."


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
