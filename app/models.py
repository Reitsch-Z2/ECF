from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime
from sqlalchemy.sql import case, select
from sqlalchemy import and_
from markupsafe import Markup


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
        query = UserSetting.query.filter_by(user_id=self.id, setting_name = setting_name).first()
        return getattr(query, 'setting')

    @setting.expression                                     #TODO CHECK WHEN THE NEW USERS ARE INSERTED!
    def setting(cls, setting_name):
        return select([UserSetting.setting]).where(cls.id == UserSetting.user_id).where(UserSetting.setting_name == setting_name).as_scalar()




class UserSetting(db.Model):
    __tablename__ = 'user_setting'

    id = db.Column(db.Integer, primary_key=True)
    setting = db.Column(db.String(128))
    setting_name = db.Column(db.String(64), index=True)

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

        url = (url_for('item_edit', username=current_user.username, item=self._name, item_id=self.id))

        return Markup(f"<a href='{url}'>{self._name}</a>")
        # return self._name


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

        query_currency = self.user.setting('query currency')
        base_currency =  self.user.setting('base currency')
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

    @price.expression                                #TODO recheck
    def price(cls):
        return select([Price.price]).where(cls.id == Price.item_id).as_scalar()                 #TODO filter-out




    @hybrid_property
    def currency(self):
        return self.prices[0].currency

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