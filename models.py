from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Currency(db.Model):
    __tablename__ = 'Currency'

    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=True, unique=True)
    CurrencyName = db.Column(db.String(15), nullable=True)
    Buy = db.Column(db.REAL, nullable=True)
    Sale = db.Column(db.REAL, nullable=True)
    AvailableQuantity = db.Column(db.REAL, nullable=True)
    Date = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return '<Currency %r>' % self.CurrencyName

    def to_dict(self):
        return {
            'Id': self.Id,
            'CurrencyName': self.CurrencyName,
            'Buy': self.Buy,
            'Sale': self.Sale,
            'AvailableQuantity': self.AvailableQuantity,
            'Date': self.Date
        }


class User(db.Model):
    __tablename__ = 'User'
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=True, unique=True)
    Login = db.Column(db.String(20), nullable=True, unique=True)
    Password = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        return '<User %r>' % self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'Login': self.Login,
            'Password': self.Password
        }


class Account(db.Model):
    __tablename__ = 'Account'
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=True, unique=True)
    UserId = db.Column(db.Integer, nullable=True)
    Balance = db.Column(db.REAL, nullable=True)
    CurrencyName = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return '<Account %r>' % self.UserId

    def to_dict(self):
        return {
            'Id': self.Id,
            'UserId': self.UserId,
            'Balance': self.Balance,
            'CurrencyName': self.CurrencyName
        }


class Transactions(db.Model):
    __tablename__ = 'Transactions'
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=True, unique=True)
    UserId = db.Column(db.Integer, nullable=True)
    CurrencyFrom = db.Column(db.String(10), nullable=True)
    CurrencyTo = db.Column(db.String(10), nullable=True)
    AmountSpent = db.Column(db.REAL, nullable=True)
    ReceivedAmount = db.Column(db.REAL, nullable=True)
    Rate = db.Column(db.Integer, nullable=True)
    Commission = db.Column(db.Integer, nullable=True)
    Date = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return '<Currency %r>' % self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'UserId': self.UserId,
            'CurrencyFrom': self.CurrencyFrom,
            'CurrencyTo': self.CurrencyTo,
            'AmountSpent': self.AmountSpent,
            'ReceivedAmount': self.ReceivedAmount,
            'Rate': self.Rate,
            'Commission': self.Commission,
            'Date': self.Date
        }


class Rating(db.Model):
    __tablename__ = 'Rating'
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=True, unique=True)
    UserId = db.Column(db.Integer, nullable=True)
    CurrencyName = db.Column(db.String(10), nullable=True)
    Rating = db.Column(db.Integer, nullable=True)
    Comment = db.Column(db.String(50), nullable=True)
    Date = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return '<Currency %r>' % self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'UserId': self.UserId,
            'CurrencyName': self.CurrencyName,
            'Rating': self.Rating,
            'Comment': self.Comment,
            'Date': self.Date
        }
