from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Currency(db.Model):
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    CurrencyName = db.Column(db.String(15), nullable=False)
    Buy = db.Column(db.REAL, nullable=False)
    Sale = db.Column(db.REAL, nullable=False)
    AvailableQuantity = db.Column(db.REAL, nullable=False)
    Date = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Currency %r>' % self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'CurrencyName': self.CurrencyName,
            'Buy': self.Buy,
            'Sale': self.Sale,
            'AvailableQuantity': self.AvailableQuantity
        }


class User(db.Model):
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    Login = db.Column(db.String(20), nullable=False, unique=True)
    Password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'Login': self.Login,
            'Password': self.Password,
        }


class Account(db.Model):
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    UserId = db.Column(db.Integer, nullable=False)
    Balance = db.Column(db.REAL, nullable=False)
    CurrencyName = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Account %r>' % self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'UserId': self.UserId,
            'Balance': self.Balance,
            'CurrencyName': self.CurrencyName,
        }


class Transactions(db.Model):
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    UserId = db.Column(db.Integer, nullable=False)
    CurrencyFrom = db.Column(db.String(10), nullable=False)
    CurrencyTo = db.Column(db.String(10), nullable=False)
    AmountSpent = db.Column(db.REAL, nullable=False)
    ReceivedAmount = db.Column(db.REAL, nullable=False)
    Rate = db.Column(db.Integer, nullable=False)
    Commission = db.Column(db.Integer, nullable=False)
    Date = db.Column(db.String(10), nullable=False)

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
    Id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    UserId = db.Column(db.Integer, nullable=False)
    CurrencyName = db.Column(db.String(10), nullable=False)
    Rating = db.Column(db.Integer, nullable=False)
    Comment = db.Column(db.Text(50), nullable=False)
    Date = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Currency %r>' % self.Id

    def to_dict(self):
        return {
            'Id': self.Id,
            'UserId': self.UserId,
            'CurrencyName': self.CurrencyName,
            'Rating': self.Rating,
            'Comment': self.Comment,
            'Date': self.Date,
        }
