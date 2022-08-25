from datetime import datetime
from flask import Flask, request
from models import db
from models import Currency, Account, Transactions, Rating

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///identifier.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/')
def index():
    return "Hello there! It's an exchanger!"


@app.get('/currency')
def all_currency():
    date_now = datetime.now().strftime("%d-%m-%Y")
    all_currency_info = Currency.query.filter_by(Date=date_now).all()
    return f"Currency's: {[itm.to_dict() for itm in all_currency_info]}"


@app.get('/currency/<currency_name>')
def currency(currency_name):
    date_now = datetime.now().strftime("%d-%m-%Y")
    currency_info = Currency.query.filter_by(CurrencyName=currency_name, Date=date_now).all()
    return f"{currency_name} info: {[itm.to_dict() for itm in currency_info]}"


@app.get('/currency/<currency_name1>/to/<currency_name2>')
def currency_to_currency(currency_name1, currency_name2):
    date_now = datetime.now().strftime("%d-%m-%Y")

    currency_1 = Currency.query.filter_by(CurrencyName=currency_name1, Date=date_now).first().Buy
    currency_2 = Currency.query.filter_by(CurrencyName=currency_name2, Date=date_now).first().Sale

    result_exchange = currency_1 / currency_2

    return f"Result:  {'{:.2f}'.format(result_exchange)} {currency_name2}"


@app.post('/currency/<currency_name1>/to/<currency_name2>')
def post_currency_to_currency(currency_name1, currency_name2):
    user_id = request.get_json()["UserId"]
    amount_to = request.get_json()["Amount"]
    date_now = datetime.now().strftime("%d-%m-%Y")

    user_balance = Account.query.filter_by(CurrencyName=currency_name1, UserId=user_id).first()
    currency_1_in = Currency.query.filter_by(CurrencyName=currency_name1, Date=date_now).first()
    currency_2_in = Currency.query.filter_by(CurrencyName=currency_name2, Date=date_now).first()
    res_exchanging = float("{:.2f}".format((currency_1_in.Buy * amount_to / currency_2_in.Sale)))

    """Is there enough currency2 in exchanger?"""
    if currency_2_in.AvailableQuantity >= res_exchanging:
        """Does the user have enough to exchange?"""
        if user_balance.Balance >= amount_to:
            """minus currency_name1 amount from user account"""
            updated_user_balance_1 = user_balance.Balance - amount_to
            Account.query.filter_by(UserId=user_id, CurrencyName=currency_name1).update(
                dict(Balance=updated_user_balance_1))

            """update or create currency_name2 for user account"""
            user_balance_2 = Account.query.filter_by(CurrencyName=currency_name2, UserId=user_id).first()
            if user_balance_2 is not None:
                updated_user_balance_2 = user_balance_2.Balance + res_exchanging
                Account.query.filter_by(UserId=user_id, CurrencyName=currency_name2).update(
                    dict(Balance=updated_user_balance_2))

            elif user_balance_2 is None:
                created_currency_2 = Account(UserId=user_id, Balance=res_exchanging, CurrencyName=currency_name2)
                db.session.add(created_currency_2)

            """minus currency_name2 from exchanger"""
            updated_currency_2_in = "{:.2f}".format(currency_2_in.AvailableQuantity - res_exchanging)
            Currency.query.filter_by(CurrencyName=currency_name2, Date=date_now).update(
                dict(AvailableQuantity=updated_currency_2_in))

            """plus currency_name1 to exchanger"""
            updated_currency_1_in = currency_1_in.AvailableQuantity + amount_to
            Currency.query.filter_by(CurrencyName=currency_name1, Date=date_now).update(
                dict(AvailableQuantity=updated_currency_1_in))

            """save transaction"""
            rate = float("{:.2f}".format((res_exchanging / amount_to)))
            commission = 0

            rating = Transactions(UserId=user_id, CurrencyFrom=currency_name1, CurrencyTo=currency_name2,
                                  AmountSpent=amount_to, ReceivedAmount=res_exchanging, Rate=rate,
                                  Commission=commission, Date=date_now)
            db.session.add(rating)

            """commit all"""
            db.session.commit()
            return "Transaction is successful"
        else:
            return "User doesn't have enough money or wrong username or wrong user_currency"
    else:
        return f"Exchanger doesn't have enough: {currency_name2}"


@app.get('/user/<user_id>')
def user_info(user_id):
    info = Account.query.filter_by(UserId=user_id).all()
    return f"User info {[itm.to_dict() for itm in info]}"


@app.get('/user/<user_id>/history')
def user_history(user_id):
    history = Transactions.query.filter_by(UserId=user_id).order_by(Transactions.Date.desc()).all()
    return f"History: {[itm.to_dict() for itm in history]}"


@app.get('/currency/<currency_name>/rating')
def get_currency_rating(currency_name):
    all_ratings = Rating.query.filter_by(CurrencyName=currency_name).all()
    return f"Rating {currency_name}: {[itm.to_dict() for itm in all_ratings]}"


@app.route('/currency/<currency_name>/rating', methods=['POST', 'PUT', 'DELETE'])
def currency_rating(currency_name):
    request_data = request.get_json()
    user_id = request_data['UserId']
    comment = request_data['Comment']
    rating = request_data['Rating']
    date_now = datetime.now().strftime("%d-%m-%Y")

    """users all comment/rating to the specified currency"""
    user_rating = Rating.query.filter_by(UserId=user_id, CurrencyName=currency_name).first()

    if request.method == "DELETE":
        db.session.delete(user_rating)
        db.session.commit()
        return "The rating and comment are deleted."

    elif request.method == "POST" or "PUT":

        if user_rating is not None:
            Rating.query.filter_by(UserId=user_id, CurrencyName=currency_name).update(
                dict(Rating=rating, Comment=comment, Date=date_now))
            db.session.commit()
            return "The rating and comment are edited."

        elif user_rating is None:
            new_rating = Rating(UserId=user_id, CurrencyName=currency_name, Rating=rating, Comment=comment,
                                Date=date_now)
            db.session.add(new_rating)
            db.session.commit()
            return "The rating and comment are added."


if __name__ == '__main__':
    app.run(debug=True)
