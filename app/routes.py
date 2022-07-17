from app import app, db
from app.models import User, Item, Category, Price
from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, ItemForm

import json



# class AjaxQuery()




@app.route('/api/tables', methods=['POST'])
def tables():
    requests = dict(json.loads(request.get_data()))

    # x = user.query.join(user_settings, users.id == user_settings.user_id)
    x = Item.query.filter_by(name = 'cvekla').all()

    return {
        # 'data' : str(x[0].category.name)
        'data': str(requests)
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
            currency = form.currency.data
        )

        category = Category.query.filter_by(name=form.category.data).first()
        if category is None:
            category = Category(
                name = form.category.data
            )


        item.prices.append(price)
        category.items.append(item)
        current_user.categories.append(category)
        current_user.items.append(item)
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
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username='Marko').first()
    login_user(user, remember=True)
    form=ItemForm()
    return redirect(url_for('entries'))




