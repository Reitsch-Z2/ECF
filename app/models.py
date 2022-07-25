from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime
from sqlalchemy.sql import case, select
from sqlalchemy import and_

from app.utils.mixins import Upmodel

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




class Item(db.Model, Upmodel):
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), index=True)
    date = db.Column(db.Date, index=True, default=datetime.utcnow)              #TODO maybe a string?
    #pseudo_count                  ####TODO - unique denoting of an element!

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))               #TODO nullable=false?
    _category = db.relationship('Category', back_populates='items', innerjoin=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='items')
    prices = db.relationship('Price', back_populates='item')

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, item_name):
        self._name = item_name

    @name.expression                                #TODO recheck
    def name(cls):
        return cls._name

    @hybrid_property
    def category(self):
        return self._category.name

    @category.setter
    def category(self, category_object):
        self._category = category_object

    @category.expression                                #TODO recheck
    def category(cls):
        return select([Category.name]).where(cls.category_id == Category.id).as_scalar()

    @hybrid_property
    def price(self):
        return str(round(self.prices[0].price, 2)) + ' ' + self.prices[0].currency              #TODO filter-out

    @price.setter
    def price(self, price_object):
        self.prices.append(price_object)

    @price.expression                                #TODO recheck
    def price(cls):
        return select([Price.price]).where(cls.id == Price.item_id).as_scalar()                 #TODO filter-out

    @hybrid_property
    def currency(self):
        return self.prices[0].currency

    # @currency.setter
    # def currency(self, item_currency):
    #     self._currency = item_currency

    @currency.expression                                #TODO recheck
    def currency(cls):
        return select([Price.currency]).where(cls.id == Price.item_id).as_scalar()


class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric)                         #TODO Float?
    currency = db.Column(db.String(64))
    first_entry = db.Column(db.Boolean, default=False)

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))  # TODO nullable=false?
    item = db.relationship('Item', back_populates='prices')



class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    items = db.relationship('Item', back_populates='_category')      #TODO lazy though?
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='categories')