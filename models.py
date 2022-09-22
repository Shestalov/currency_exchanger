from sqlalchemy import Column, Integer, REAL, String, Float
from database import Base


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    currency_name = Column(String(15), nullable=False)
    buy = Column(REAL, nullable=False)
    sale = Column(REAL, nullable=False)
    available_quantity = Column(REAL, nullable=False)
    date = Column(String(10), nullable=False)

    def __repr__(self):
        return '<Currency %r>' % self.currency_name

    def to_dict(self):
        return {
            'id': self.id,
            'currency_name': self.currency_name,
            'buy': self.buy,
            'sale': self.sale,
            'available_quantity': self.available_quantity,
            'date': self.date
        }


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    login = Column(String(20), nullable=False, unique=True)
    password = Column(String(30), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.Id

    def to_dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'password': self.password
        }


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    user_login = Column(String(50), nullable=False)
    balance = Column(REAL, nullable=False)
    currency_name = Column(String(10), nullable=False)

    def __repr__(self):
        return '<Account %r>' % self.user_login

    def to_dict(self):
        return {
            'id': self.id,
            'user_login': self.user_login,
            'balance': self.balance,
            'currency_name': self.currency_name
        }


class Transactions(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    user_login = Column(String(50), nullable=False)
    currency_from = Column(String(10), nullable=False)
    currency_to = Column(String(10), nullable=False)
    amount_spent = Column(REAL, nullable=False)
    received_amount = Column(REAL, nullable=False)
    rate = Column(Float, nullable=False)
    commission = Column(Integer, nullable=False)
    date = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False)
    transaction_id = Column(String(100), nullable=False)

    def __repr__(self):
        return '<Transaction %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'user_login': self.user_login,
            'currency_from': self.currency_from,
            'currency_to': self.currency_to,
            'amount_spent': self.amount_spent,
            'received_amount': self.received_amount,
            'rate': self.rate,
            'commission': self.commission,
            'date': self.date,
            'status': self.status,
            'transaction_id': self.transaction_id
        }


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    user_login = Column(String(50), nullable=False)
    currency_name = Column(String(10), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(50), nullable=False)
    date = Column(String(10), nullable=False)

    def __repr__(self):
        return '<Currency name %r>' % self.currency_name

    def to_dict(self):
        return {
            'id': self.id,
            'user_login': self.user_login,
            'currency_name': self.currency_name,
            'rating': self.rating,
            'comment': self.comment,
            'date': self.date
        }

