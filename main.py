import uuid
import sqlalchemy
import database
import models
import datetime
from flask import Flask, request, session, render_template, url_for, redirect
from celery_worker import task

app = Flask(__name__)
app.secret_key = "very_secret_key"


@app.route('/')
def index():
    return {"status": "Ok"}


@app.get('/currency')
def all_currency():
    database.init_db()
    date_now = datetime.datetime.now().strftime('%d-%m-%Y')
    all_currency_info = models.Currency.query.filter_by(date=date_now).all()
    return [itm.to_dict() for itm in all_currency_info]


@app.get('/currency/<currency_name>')
def currency(currency_name: str):
    database.init_db()
    date_now = datetime.datetime.now().strftime('%d-%m-%Y')
    currency_info = models.Currency.query.filter_by(currency_name=currency_name, date=date_now).all()
    if len(currency_info) > 0:
        return [itm.to_dict() for itm in currency_info]
    else:
        return {"error": "invalid_currency"}


@app.get('/currency/<currency_name>/rating')
def get_currency_rating(currency_name: str):
    database.init_db()
    all_ratings = models.Rating.query.filter_by(currency_name=currency_name).all()

    avr_rating = dict(database.db_session.query(sqlalchemy.func.avg(models.Rating.rating).label('rating')).filter(
        models.Rating.currency_name == currency_name).first())['rating']

    if len(all_ratings) > 0:
        return {"currency name": currency_name, "average": avr_rating, "all_rating": [i.to_dict() for i in all_ratings]}
    else:
        return {"error": "no rating"}


@app.route('/currency/<currency_name>/rating', methods=['POST', 'PUT', 'DELETE'])
def currency_rating(currency_name: str):
    database.init_db()
    request_data = request.get_json()
    user_login = request_data['user_login']
    comment = request_data['comment']
    rating = request_data['rating']
    date_now = datetime.datetime.now().strftime('%d-%m-%Y')

    """users all comment/rating to the specified currency"""
    user_rating = models.Rating.query.filter_by(user_login=user_login, currency_name=currency_name).first()

    if request.method == 'DELETE':
        database.db_session.delete(user_rating)
        database.db_session.commit()
        return {"status": "The rating and comment are deleted"}

    elif request.method == 'POST':
        new_rating = models.Rating(user_login=user_login, currency_name=currency_name, rating=rating,
                                   comment=comment,
                                   date=date_now)
        database.db_session.add(new_rating)
        database.db_session.commit()
        return {"status": "The rating and comment are added"}

    elif request.method == 'PUT':
        models.Rating.query.filter_by(user_login=user_login, currency_name=currency_name).update(
            dict(rating=rating, comment=comment, date=date_now))
        database.db_session.commit()
        return {"status": "The rating and comment are edited"}


@app.get('/currency/<currency_name1>/to/<currency_name2>')
def init_transaction(currency_name1: str, currency_name2: str):
    if session.get('user_name') is not None:
        return render_template('amount.html')
    else:
        return {"error": "need login first"}


@app.post('/currency/<currency_name1>/to/<currency_name2>')
def post_currency_to_currency(currency_name1: str, currency_name2: str):
    user_login = session.get('user_name')
    amount_to = float(request.form.get('amount_to'))

    database.init_db()
    transaction_id = str(uuid.uuid4())
    date_now = datetime.datetime.now().strftime('%d-%m-%Y')
    transaction = models.Transactions(user_login=user_login, currency_from=currency_name1, currency_to=currency_name2,
                                      amount_spent=amount_to, received_amount=0, rate=0,
                                      commission=0, date=date_now, status="in_processing",
                                      transaction_id=transaction_id)
    database.db_session.add(transaction)
    database.db_session.commit()

    task_obj = task.apply_async(args=[user_login, amount_to, currency_name1, currency_name2, transaction_id])
    return {"task_id": str(task_obj)}


@app.route('/user', methods=['GET', 'POST'])
def user_info():
    database.init_db()

    if request.method == 'GET':
        user_name = session.get('user_name')

        if user_name is None:
            return render_template('login.html')
        else:
            info = models.Account.query.filter_by(user_login=user_name).all()
            return [itm.to_dict() for itm in info]

    if request.method == 'POST':
        user_login = request.form.get('uname')
        user_password = request.form.get('psw')
        user_info_creds = models.User.query.filter_by(login=user_login, password=user_password).first()

        if user_info_creds:
            session['user_name'] = user_login
            return {"status": "login successful"}
        else:
            return {"status": "login not successful"}


@app.get('/user/history')
def user_history():
    user_login = session.get('user_name')

    if session.get('user_name') is not None:
        database.init_db()
        history = models.Transactions.query.filter_by(user_login=user_login).order_by(
            models.Transactions.date.desc()).all()
        if len(history) > 0:
            return [itm.to_dict() for itm in history]
        else:
            return {user_login: "history empty"}
    else:
        return {"error": "login first"}


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
