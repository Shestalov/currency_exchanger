import sqlite3
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

DATE_NOW = datetime.now().strftime("%d-%m-%Y")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_connect_database(query):
    with sqlite3.connect('identifier.sqlite') as conn:
        conn.row_factory = dict_factory
        conn.commit()
        cursor = conn.execute(query)
        res = cursor.fetchall()
        return res


@app.route('/')
def index():
    return "Hello there! It's an exchanger!"


# all currencies (buy, sale)
@app.get('/currency')
def all_currency():
    all_currency_info = get_connect_database(f"""SELECT CurrencyName, Buy, Sale, AvailableQuantity FROM Currency 
                                                    WHERE Date='{DATE_NOW}';""")
    return f"Here are all the currency's: {all_currency_info} on {DATE_NOW}"


@app.get('/currency/<currency_name>')
def currency(currency_name):
    currency_info = get_connect_database(f"""SELECT CurrencyName, Buy, Sale, AvailableQuantity 
                                                FROM Currency WHERE CurrencyName = '{currency_name}' 
                                                AND Date='{DATE_NOW}';""")
    return f"Currency info: {currency_info} on {DATE_NOW}"


# currency -> uah -> currency
@app.get('/currency/<currency_name1>/to/<currency_name2>')
def currency_to_currency(currency_name1, currency_name2):
    result_exchange = get_connect_database(f"""SELECT (
                                                (SELECT Buy FROM Currency 
                                                WHERE CurrencyName = '{currency_name1}' AND Date='{DATE_NOW}') /
                                                (SELECT Sale FROM Currency 
                                                WHERE CurrencyName = '{currency_name2}' AND Date='{DATE_NOW}')) 
                                                AS '{currency_name2}';""")
    return f"{result_exchange} on {DATE_NOW}"


@app.post('/currency/<currency_name1>/to/<currency_name2>')
def post_currency_to_currency(currency_name1, currency_name2):
    user_id = request.get_json()["UserId"]
    amount_to_exchange = request.get_json()["Amount"]

    # example [{'CurrencyName': 'usd', 'Balance': 900}, {'CurrencyName': 'eur', 'Balance': 97}]
    user_balance = get_connect_database(f"""SELECT CurrencyName, Balance FROM Account WHERE UserId='{user_id}';""")

    # example [{'eur': 97.43101343101343}]
    need_currency2 = get_connect_database(f"""SELECT ((SELECT Buy FROM Currency WHERE CurrencyName = '{currency_name1}' 
                                                AND Date='{DATE_NOW}') 
                                                
                                                * '{amount_to_exchange}' / 
                                                
                                                (SELECT Sale FROM Currency WHERE CurrencyName = '{currency_name2}' 
                                                 AND Date='{DATE_NOW}')) 
                                                 
                                                 AS '{currency_name2}';""")

    # example [{'eur': 8000}]
    currency2_in_exchanger = get_connect_database(f"""SELECT AvailableQuantity AS '{currency_name2}' 
                                                                FROM Currency WHERE CurrencyName='{currency_name2}' 
                                                                AND Date='{DATE_NOW}';""")

    # чи в обміннику вистачає валюти для обміну
    if currency2_in_exchanger[0][f"{currency_name2}"] >= need_currency2[0][f"{currency_name2}"]:
        # чи у юзера вистачає валюти для обміну та чи обрана валюта співпадає з тим що у юзера в акаунті
        for currency_1 in user_balance:
            if currency_1["CurrencyName"] == f"{currency_name1}" and currency_1["Balance"] >= amount_to_exchange:

                # відняти суму обміну у юзера
                balance = currency_1["Balance"] - amount_to_exchange
                get_connect_database(f"""UPDATE Account SET Balance='{balance}'
                                            WHERE CurrencyName='{currency_name1}' AND UserId='{user_id}';""")

                # додати або створити нову валюту для юзера в акаунті
                # якщо у юзера більше однієї валюти в акаунті
                if len(user_balance) > 1:
                    for currency_2 in user_balance:
                        if currency_2["CurrencyName"] == f"{currency_name2}":
                            new_balance = currency_2["Balance"] + need_currency2[0][f"{currency_name2}"]
                            get_connect_database(f"""UPDATE Account SET Balance='{round(new_balance)}'
                                                        WHERE CurrencyName='{currency_name2}' AND UserId='{user_id}';""")
                # якщо відсутня валюта в акаунті для отримання то створити нову
                else:
                    get_connect_database(f"""INSERT INTO Account (UserId, Balance, CurrencyName)
                                                VALUES ('{user_id}', '{need_currency2[0][f'{currency_name2}']}',
                                                        '{currency_name2}');""")

                # віднімання виданої валюти з обмінника
                currency2_in = currency2_in_exchanger[0][f"{currency_name2}"] - amount_to_exchange

                get_connect_database(f"""UPDATE Currency SET AvailableQuantity='{currency2_in}' 
                                            WHERE Date='{DATE_NOW}' AND CurrencyName='{currency_name2}';""")

                # додавання отриманої валюти у обмінник, example [{'usd': 10000}]
                currency1_in_exchanger = get_connect_database(f"""SELECT AvailableQuantity AS '{currency_name1}'
                                                                    FROM Currency WHERE CurrencyName='{currency_name1}' 
                                                                    AND Date='{DATE_NOW}' ;""")

                receive_in_exchanger = currency1_in_exchanger[0][f"{currency_name1}"] + amount_to_exchange

                get_connect_database(f"""UPDATE Currency SET AvailableQuantity='{receive_in_exchanger}' 
                                         WHERE Date='{DATE_NOW}' AND CurrencyName='{currency_name1}';""")

                # rate for transaction history
                rate = "{:.2f}".format((need_currency2[0][f"{currency_name2}"] / amount_to_exchange))
                commission = 10
                # save transaction
                get_connect_database(f"""INSERT INTO Transactions (UserId, CurrencyFrom, CurrencyTo, AmountSpent, 
                                                                    ReceivedAmount, Rate, Commission, Date) 
                                                VALUES ('{user_id}', '{currency_name1}', '{currency_name2}', 
                                                        '{amount_to_exchange}', 
                                                        '{"{:.2f}".format(need_currency2[0][f'{currency_name2}'])}', 
                                                        '{rate}', '{commission}', '{DATE_NOW}')""")

                return "Transaction is successful"
            else:
                return "User doesn't have enough money or wrong username or wrong user_currency"
        else:
            return f"Exchanger doesn't have enough: {currency_name2}"


# user info (example user_id = 101)
@app.get('/user/<user_id>')
def user_info(user_id):
    info = get_connect_database(f"""SELECT UserId, Balance, CurrencyName FROM Account WHERE UserId = '{user_id}';""")
    return f"User info {info}"


@app.get('/user/<user_id>/history')
def user_history(user_id):
    history = get_connect_database(f"""SELECT CurrencyFrom, CurrencyTo, AmountSpent, 
                                                    Rate, ReceivedAmount, Commission, Date
                                            FROM Transactions WHERE UserId='{user_id}';""")
    return f"History: {history}"


@app.get('/currency/<currency_name>/rating')
def currency_rating(currency_name):
    rating = get_connect_database(f"""SELECT Rating, Comment, Date FROM Rating 
                                        WHERE Rating.CurrencyName='{currency_name}';""")
    return f"Rating {currency_name}: {rating}"


@app.post('/currency/<currency_name>/rating')
def add_currency_rating(currency_name):
    request_data = request.get_json()
    user_id = request_data['UserId']
    comment = request_data['Comment']
    rating = request_data['Rating']

    get_connect_database(f"""INSERT INTO Rating (UserId, CurrencyName, Rating, Comment, Date) 
                                    VALUES ('{int(user_id)}', '{currency_name}', '{rating}', 
                                            '{comment}', '{DATE_NOW}');""")

    return "The rating and comment are added."

# [{'CurrencyName': 'usd', 'UserId': 101}, {'CurrencyName': 'eur', 'UserId': 101}]
# [{'UserId': 101, 'CurrencyName': 'usd'}]
# @app.route('/test')
# def test():
#     all_rating = get_connect_database(f"""SELECT CurrencyName,UserId  FROM Rating WHERE UserId='101';""")
#     return f"ok {all_rating}"


if __name__ == '__main__':
    app.run(debug=True)
