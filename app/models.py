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
        """User method used to return back the value of a setting based on the setting name passed as the argument"""
        query = UserSetting.query.filter_by(user_id=self.id, setting_name=setting_name).first()
        return getattr(query, 'setting')

    def set_setting(self, setting_name, setting_value):
        """User method used to edit/create a user settings based on the setting name + value passed as the arguments"""
        new_setting = UserSetting.query.filter_by(user_id=self.id, setting_name=setting_name).first()
        if new_setting == None:
            new_setting = UserSetting(setting_name=setting_name, setting=setting_value)
            self.settings.append(new_setting)
        else:
            new_setting.setting = setting_value

    @setting.expression
    def setting(cls, setting_name):
        """Expression used to return the value of a setting for the passed in setting name when querying the database"""
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
        """Item property used to return the item name formatted as a unique URL as a link for the item edit page"""
        url = (url_for('item_edit', username=current_user.username, item=self.name, item_id=self.id))
        return f"<a href='{url}'>{self.name}</a>"

    @item.expression
    def item(cls):
        """Expression used to return the name of the item when querying the database"""
        return cls.name

    @hybrid_property
    def category(self):
        """
        Item property used to return the name of the category for the item (since the "_property" attribute defined
        above returns the category object from the database, because "_property" defines the item-category db
        relationship). This hybrid property is used for displaying the category name in the table with the queried
        results, where the non-underscore naming here is used as a column name for displaying the property name value
        (key-value structure, both of which are displayed in the table).
        """
        return self._category.name

    @category.expression
    def category(cls):
        """Expression used to return the name of the category when querying the database"""
        return select([Category.name]).where(cls.category_id == Category.id).as_scalar()

    @category.setter
    def category(self, category_object):
        """Setter method for creating a relationship between the item and the category"""
        self._category = category_object

    @hybrid_property
    def price(self):
        """
        Hybrid property that returns the price for the item based on the saved user setting for the type of the currency
        query. In case there are multiple prices, the setting which is retrieved from the database has the effect on
        which of the multiple prices should get returned. If the user queries by "Total - base currency" option, the
        price in the main/base currency is returned. If the user uses "Total - combined currencies", only the price
        which was entered first/originally is returned, regardless of the currency (checked via the "first_entry"
        boolean property for that price). If the user makes a query by a specific currency (USD/EUR...), the price
        which was both the first price entered, while also being in that currency, is returned (which means that there
        are no common/shared items between queries made for specific currencies).

        If the user makes a query for results showing multiple currencies at once, the price amount gets a suffix with
        the currency code, so that the user can discern which prices are in which currency. For all other queries, all
        the results are for a single chosen currency, and therefore only the price amount is displayed.
        """

        base_currency = self.user.setting('base_currency')
        query_currency = self.user.setting('query_currency')
        if query_currency == 'Total - base currency':                                       #TODO maybe all as list
            price = list(filter(lambda x: x.currency == base_currency, self.prices))[0]     # comprehensions? Filter +
        elif query_currency == 'Total - combined currencies':                               # lambda make it more clear/
            price = list(filter(lambda x: x.first_entry == True, self.prices))[0]           # readable though
        else:
            price = list(filter(lambda x: x.currency == query_currency and x.first_entry == True, self.prices))[0]

        if query_currency == 'Total - combined currencies':
            return str(round(price.price, 2)) + ' ' + price.currency
        else :
            return str(round(price.price, 2))

    @price.expression
    def price(cls):
        """Expression used to return the price for the item when querying the database"""
        return select([Price.price]).where(cls.id == Price.item_id).as_scalar()

    @price.setter
    def price(self, price_object):
        """Setter method used to update/enter the price for the item"""
        self.prices.append(price_object)

    # @hybrid_property
    # def currency(self):
    #     """Hybrid property used to return the currency for item price -  """      #TODO
    #     return self.prices[0].currency
    # @currency.expression
    # def currency(cls):
    #     return select([Price.currency]).where(cls.id == Price.item_id).as_scalar()


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
    #a multicolumn index made for the column/user, so that no double category entries for the user can be made;
    # unique index on category column only would not work, since multiple users can have categories with identical names
    __table_args__ = (db.Index('index_category_user', 'name', 'user_id', unique=True),)
