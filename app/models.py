from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    settings = db.relationship('UserSettings', back_populates='users')
    items = db.relationship('Item', back_populates='user')
    categories = db.relationship('Category', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)
    settings = db.Column(db.PickleType)
    settings_name = db.Column(db.String(64), index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.relationship("User", back_populates="settings")


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date = db.Column(db.Date, index=True, default=datetime.utcnow)              #TODO maybe a string?

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))               #TODO nullable=false?
    category = db.relationship('Category', back_populates='items', innerjoin=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='items')
    prices = db.relationship('Price', back_populates='item')

    # @hybrid_property
    # def categori(self):
    #     return self.category.name
    #
    # @categori.expression
    # def categori(cls):
    #     return select([Category.name]).where(cls.category_id == Category.id).as_scalar()

class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric)                         #TODO Float?
    currency = db.Column(db.String(64))

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))  # TODO nullable=false?
    item = db.relationship('Item', back_populates='prices')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    items = db.relationship('Item', back_populates='category')      #TODO lazy though?
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='categories')