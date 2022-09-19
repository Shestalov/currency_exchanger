import os
import models
import datetime
import database
from celery import Celery

app = Celery('celery_worker', broker=os.environ.get("RABBIT_CONNECTION_STR"))


def change_status_transaction(transaction_id: str, res_exchanging: float, rate: float, commission: int, date_now: str,
                              status: str):
    models.Transactions.query.filter_by(transaction_id=transaction_id).update(
        dict(received_amount=res_exchanging, rate=rate, commission=commission, status=status, date=date_now))


@app.task()
def task(user_id: int, amount_to: float, currency_name1: str, currency_name2: str, transaction_id: str) -> str:
    database.init_db()

    date_now = datetime.datetime.now().strftime("%d-%m-%Y")

    user_balance = models.Account.query.filter_by(currency_name=currency_name1, user_id=user_id).first()
    currency_1_in = models.Currency.query.filter_by(currency_name=currency_name1, date=date_now).first()
    currency_2_in = models.Currency.query.filter_by(currency_name=currency_name2, date=date_now).first()
    res_exchanging = float("{:.2f}".format((currency_1_in.buy * amount_to / currency_2_in.sale)))
    commission = 0
    rate = float("{:.2f}".format((res_exchanging / amount_to)))

    """Is there enough currency2 in exchanger?"""
    if currency_2_in.available_quantity >= res_exchanging:

        """Does the user have enough to exchange?"""
        if user_balance.balance >= amount_to:

            """minus currency_name1 amount from user account"""
            updated_user_balance_1 = user_balance.balance - amount_to
            models.Account.query.filter_by(user_id=user_id, currency_name=currency_name1).update(
                dict(balance=updated_user_balance_1))

            """update or create currency_name2 for user account"""
            user_balance_2 = models.Account.query.filter_by(currency_name=currency_name2, user_id=user_id).first()
            if user_balance_2 is not None:
                updated_user_balance_2 = user_balance_2.balance + res_exchanging
                models.Account.query.filter_by(user_id=user_id, currency_name=currency_name2).update(
                    dict(balance=updated_user_balance_2))

            elif user_balance_2 is None:
                created_currency_2 = models.Account(user_id=user_id,
                                                    balance=res_exchanging,
                                                    currency_name=currency_name2)
                database.db_session.add(created_currency_2)

            """minus currency_name2 from exchanger"""
            updated_currency_2_in = "{:.2f}".format(currency_2_in.available_quantity - res_exchanging)
            models.Currency.query.filter_by(currency_name=currency_name2, date=date_now).update(
                dict(available_quantity=updated_currency_2_in))

            """plus currency_name1 to exchanger"""
            updated_currency_1_in = currency_1_in.available_quantity + amount_to
            models.Currency.query.filter_by(currency_name=currency_name1, date=date_now).update(
                dict(available_quantity=updated_currency_1_in))

            """change status of transaction to success"""
            status = "success"
            change_status_transaction(transaction_id, res_exchanging, rate, commission, date_now, status)

            """commit all"""
            database.db_session.commit()

            return "Transaction is successful"

        else:
            status = "user error"
            change_status_transaction(transaction_id, res_exchanging, rate, commission, date_now, status)
            database.db_session.commit()
            return "User doesn't have enough money or wrong username or wrong user_currency"

    else:
        status = "exchanger error"
        change_status_transaction(transaction_id, res_exchanging, rate, commission, date_now, status)
        database.db_session.commit()
        return f"Exchanger doesn't have enough: {currency_name2}"
