from time import time
from datetime import datetime
import jwt
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql import select
from app import app, db, login
from app.utils.mixins import Upmodel


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    settings = db.relationship('UserSetting', back_populates='users')
    items = db.relationship('Item', back_populates='user')
    categories = db.relationship('Category', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @hybrid_method
    def setting(self, setting_name):
        query = UserSetting.query.filter_by(user_id=self.id, setting_name=setting_name).first()
        return getattr(query, 'setting')

    def set_setting(self, setting_name, setting_value):
        new_setting = UserSetting.query.filter_by(user_id=self.id, setting_name=setting_name).first()
        if new_setting == None:
            new_setting = UserSetting(setting_name=setting_name, setting=setting_value)
            self.settings.append(new_setting)
        else:
            new_setting.setting = setting_value

    @setting.expression
    def setting(cls, setting_name):
        return select([UserSetting.setting]).where(cls.id == UserSetting.user_id).where(
            UserSetting.setting_name == setting_name).as_scalar()

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'],
            algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class UserSetting(db.Model):
    __tablename__ = 'user_setting'
    id = db.Column(db.Integer, primary_key=True)
    setting = db.Column(db.String(128))
    setting_name = db.Column(db.String(64), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.relationship("User", back_populates="settings")


class Item(db.Model, Upmodel):
    id = db.Column(db.Integer, primary_key=True)                # TODO - unique denoting of an element! UUID in Postgres
    name = db.Column(db.String(64), index=True)
    date = db.Column(db.Date, index=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    _category = db.relationship('Category', back_populates='items', innerjoin=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='items')
    prices = db.relationship('Price', back_populates='item', cascade="all, delete")

    @hybrid_property
    def item(self):
        url = (url_for('item_edit', username=current_user.username, item=self.name, item_id=self.id))
        return f"<a href='{url}'>{self.name}</a>"

    @item.expression
    def item(cls):
        return cls.name

    @hybrid_property
    def category(self):
        return self._category.name

    @category.expression
    def category(cls):
        return select([Category.name]).where(cls.category_id == Category.id).as_scalar()

    @category.setter
    def category(self, category_object):
        self._category = category_object

    @hybrid_property
    def price(self):
        query_currency = self.user.setting('query_currency')
        base_currency = self.user.setting('base_currency')
        if query_currency == 'Total - base currency':
            price = list(filter(lambda x: x.currency == base_currency, self.prices))[0]
        elif query_currency == 'Total - combined currencies':
            price = list(filter(lambda x: x.first_entry == True, self.prices))[0]
        else:
            price = list(filter(lambda x: x.currency == query_currency and x.first_entry == True, self.prices))[0]
        return str(round(price.price, 2)) + ' ' + price.currency

    @price.setter
    def price(self, price_object):
        self.prices.append(price_object)

    @price.expression
    def price(cls):
        return select([Price.price]).where(cls.id == Price.item_id).as_scalar()

    @hybrid_property
    def currency(self):
        return self.prices[0].currency

    @currency.expression
    def currency(cls):
        return select([Price.currency]).where(cls.id == Price.item_id).as_scalar()


class Price(db.Model, Upmodel):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric)  # TODO Float?
    currency = db.Column(db.String(64))
    first_entry = db.Column(db.Boolean, default=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship('Item', back_populates='prices')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    items = db.relationship('Item', back_populates='_category')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='categories')
    __table_args__ = (db.Index('index_category_user', 'name', 'user_id', unique=True),)
