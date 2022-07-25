from app import app, db
from app.models import User, Item, Category, Price
from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, ItemForm

import json

from sqlalchemy import func
from datetime import datetime

from app.utils.orms import AjaxQuery
from app.utils.helpers import currency_converter_api




@app.route('/api/auto-suggest', methods=['POST'])
@login_required
def autosuggest():

    requests = dict(json.loads(request.get_data()))
    property = requests['property']
    value = requests['value']


    test = User.query.filter_by(id = current_user.id).first()
    lista = getattr(test, property)
    lista = [element.name for element in lista if element.name.lower().startswith(value.lower())]
    lista = list(dict.fromkeys(lista))

    return {
        'data': lista

    }

@app.route('/api/auto-fill', methods=['POST'])
@login_required
def autofill():

    requests = dict(json.loads(request.get_data()))                     #TODO model dictionary at the beginning,
    property = requests['property']                                     # as to not hardcode model name
    value = requests['value']

    test = Item.query.filter_by(user_id = current_user.id, name = value).first()
    aufofill_value = getattr(test, property)

    return {
        'data': str(aufofill_value)
    }



@app.route('/api/tables', methods=['POST'])
@login_required
def tables():
    requests = dict(json.loads(request.get_data()))
    columns = ['name', 'price', 'currency']
    # filters = {'name' : 'dezodorans'}                 #TODO TURN INTO COMBINATION OF MODES FOR FILTERING OUT!

    dates=requests['data']['time']
    # AQ = AjaxQuery(dates)

    columns = ['name', 'category', 'price', 'date']

    test = AjaxQuery(requests)
    test = test.querier(columns)

    # dime = datetime.strptime('21 June, 2018', "%d %B, %Y")
    # x = user.query.join(user_settings, users.id == user_settings.user_id)
    # x = Item.query.filter_by(date >= '2022/02/02').all()
    # x = Item.query.filter_by(name= 'cvekla').all()

    # Query = Item.query.
    # x = Item.query.filter(Item.date >= '2022-07-17').filter_by(name='cvekla').all()


    # x = Item.query.filter(Item.date >= '2022-07-17').filter_by(name='cvekla').all()               #proper


    # x = Item.query.filter(Item.date.between('2022-07-17', '2022-09-17')).all()                      #proper

    # x = Item.query.filter_by(user_id = current_user.id).all()

    # for item in x.prices:
    #     if item.currency == 'RSD':
    #         final = x
    # xx = x.to_dict(['name',['price', 'RSD'], 'category'])



    return {
        'data': test
        # 'data' : AjaxQuery.to_dict_mapper(x, columns)
        # 'data': str(x[0].to_dict(columns))
    }

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template('entries.html', form=ItemForm())
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfuly registered your account')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return render_template('entries.html', form=ItemForm())
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('entries'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/')
@app.route('/index')                                                #TODO why???
@app.route('/entries', methods=['GET', 'POST'])

@login_required

def entries():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(
            name = form.item.data,
            date = form.date.data
        )

        price = Price(
            price = form.price.data,
            currency = form.currency.data,
            first_entry = True
        )

        currency = form.currency.data
        if  currency != 'RSD':                      #TODO try block + de-hardcode

            converted_price = currency_converter_api(currency, 'RSD', form.date.data, form.price.data)
            price2 = Price(
                price=converted_price,
                currency='RSD',
                first_entry=False
            )
            item.prices.append(price2)





        category = Category.query.filter_by(name=form.category.data, user_id=current_user.id).first()            #TODO superfluous? re-check
        if category is None:
            category = Category(
                name = form.category.data
            )




        item.prices.append(price)
        category.items.append(item)
        current_user.categories.append(category)
        current_user.items.append(item)

        update_categories = Item.query.filter_by(name=form.item.data, user_id=current_user.id).all()
        for item in update_categories:
            item.category = category
            db.session.add(item)

        db.session.commit()
        return redirect(url_for('entries'))


    return render_template('entries.html', form=form)


@app.route('/overview')

def overview():
    form = ItemForm()
    return render_template('overview.html', form=form)

@app.route('/inception', methods=['GET', 'POST'])
def inception():
    user = User(username='Marko', email='marko@ecf.com')
    user.set_password('Alesund')

    # item = Item(
    #     name='cvekla',
    #     date='2022/07/018'
    # )
    #
    # price = Price(
    #     price=320,
    #     currency='RSD'
    # )
    #
    # category = Category.query.filter_by(name=form.category.data).first()
    # if category is None:
    #     category = Category(
    #         name=form.category.data
    #     )
    #
    # item.prices.append(price)
    # category.items.append(item)
    # current_user.categories.append(category)
    # current_user.items.append(item)
    # db.session.commit()









    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username='Marko').first()
    login_user(user, remember=True)
    form=ItemForm()
    return redirect(url_for('entries'))




