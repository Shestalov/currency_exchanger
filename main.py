import sqlite3
from flask import Flask

app = Flask(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_connect_database(query):
    with sqlite3.connect('identifier.sqlite') as conn:
        conn.row_factory = dict_factory
        cursor = conn.execute(query)
        res = cursor.fetchall()
        return res


@app.route('/')
def index():
    return "Hello there! It's an exchanger!"


# усі валюти (купівля, продаж)
@app.get('/currency')
def get_all_currency():
    currency = get_connect_database("""SELECT CurrencyName, Buy, Sale, AvailableQuantity FROM Currency""")
    return f"Here are all the currency's: {currency}"


# вибраний курс (купівля ТА продаж) # POST ?
@app.get('/currency/<currency_name>')
def get_currency(currency_name):
    currency = get_connect_database(f"""SELECT CurrencyName, Buy, Sale, AvailableQuantity 
                                        FROM Currency WHERE CurrencyName = '{currency_name}'""")
    return f"Currency info: {currency}"


# Валюта -> гривня -> валюта.
@app.get('/currency/<currency_name1>/to/<currency_name2>')
def get_currency_to_currency(currency_name1, currency_name2):
    res = get_connect_database(f"""SELECT (
                                    (SELECT Buy FROM Currency WHERE CurrencyName = '{currency_name1}') /
                                    (SELECT Sale FROM Currency WHERE CurrencyName = '{currency_name2}')
                                    ) AS {currency_name2}""")
    return f"{res}"


@app.post('/currency/<currency_name1>/to/<currency_name2>')
def post_currency_to_currency():
    ...


# інфо по юзер ід
@app.get('/user/<user_id>')
def user(user_id):
    res = get_connect_database(f"""SELECT User.Login, Account.Balance, Currency.CurrencyName
                                    FROM User INNER JOIN Account INNER JOIN Currency ON Account.UserId = User.Id 
                                    AND Account.CurrencyId=Currency.Id
                                    WHERE User.Id = '{user_id}';""")
    return f"User info {res}"


@app.get('/user/<user_id>/history')
def user_history(user_id):
    res = get_connect_database(f"""SELECT CurrencyFrom, CurrencyTo, AmountSpent, Rate, ReceivedAmount, Commission, 
                                            DateTime FROM Transactions WHERE UserId='{user_id}';""")
    return f"History: {res}"


if __name__ == '__main__':
    app.run(debug=True)
