import json
from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, ItemForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User, Item, Category, Price, UserSetting
from app.utils.orms import AjaxQuery
from app.utils.helpers import currency_converter_api, json_loader


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
    return {'data': lista}

@app.route('/api/auto-fill', methods=['POST'])
@login_required
def autofill():
    requests = dict(json.loads(request.get_data()))                     #TODO model dictionary at the beginning,
    property = requests['property']                                     # as to not hardcode model name
    value = requests['value']
    test = Item.query.filter_by(user_id = current_user.id, name = value).first()
    aufofill_value = getattr(test, property)
    return {'data': str(aufofill_value)}

@app.route('/api/user-settings', methods=['POST'])
@login_required
def usersettings():
    requests = dict(json.loads(request.get_data()))
    setting_name = requests['setting_name']
    setting_value = requests['setting']
    setting = UserSetting.query.filter_by(user_id = current_user.id, setting_name = setting_name).first()

    #TODO if setting is NONE!

    setting.setting = setting_value
    db.session.add(setting)
    db.session.commit()
    return setting_value

@app.route('/api/tables', methods=['POST'])
@login_required
def tables():
    requests = dict(json.loads(request.get_data()))
    columns = ['item', 'category', 'price', 'date']
    test = AjaxQuery(requests)
    test = test.querier(columns)
    return {'data': test}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template('entries.html', form=ItemForm())
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        setting = UserSetting(setting_name='base currency', setting=form.currency.data)
        user.settings.append(setting)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfuly registered your account')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
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

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions how to reset your password')
            return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/entries', methods=['GET', 'POST'])
@login_required
def entries():
    base_currency = current_user.setting('base currency')
    currencies = json_loader(True, "settings", "general", "currencies")
    currencies.remove(base_currency)
    choices = [base_currency, *currencies]
    form = ItemForm()
    form.currency.choices = choices                 #TODO BRAVO! softcode it
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
        if  currency != base_currency:
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
        return redirect(url_for('overview'))
    return render_template('entries.html', form=form)

@app.route('/<username>/items/<item>/<item_id>', methods=['GET', 'POST'])
@login_required
def item_edit(username, item, item_id):




    form = ItemForm()
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    price = Price.query.filter_by(item_id=item_id, first_entry=True).first()
    category = Category.query.filter_by(id=item.category_id).first()
    # if request.form['action'] == 'Download':          #TODO submit changes/delete/cancel.... + micro modal popup confirmation

    if request.method == 'POST':

                                                                #TODO #TODO #TODO #TODO
        requested = (request.form.to_dict())
        if requested['submit'] == 'Cancel':
            return redirect(url_for('overview'))

        if requested['submit'] == 'Delete':
            prices = Price.query.filter_by(item_id=item_id).all()
            for price in prices:
                db.session.delete(price)
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('overview'))

        elif requested['submit'] == 'Edit':
            if form.validate_on_submit():
                if item.name != form.item.data or item.date != form.date.data:
                    item.name = form.item.data
                    item.date = form.date.data
                if category.name != form.category.data:
                    category = Category.query.filter_by(name=form.category.data,
                                                        user_id=current_user.id).first()  # TODO superfluous? re-check
                    if category is None:
                        category = Category(
                            name=form.category.data
                        )
                    category.items.append(item)
                if price.price != form.price.data or price.currency != form.currency.data:
                    prices = Price.query.filter_by(item_id=item_id, first_entry=0).all()
                    price.price = form.price.data
                    price.currency = form.currency.data
                    for prc in prices:
                        db.session.delete(prc)
                    base_currency = current_user.setting('base currency')
                    if price.currency != base_currency:
                        converted_price = currency_converter_api(price.currency, base_currency, form.date.data, form.price.data)
                        price2 = Price(
                            price=converted_price,
                            currency=base_currency,
                            first_entry=False
                        )
                        item.prices.append(price2)
                db.session.commit()
                return redirect(url_for('overview'))
    elif request.method == "GET":
        form.item.data = item.name
        form.price.data = price.price
        form.currency.data = price.currency
        form.category.data = item.category
        form.date.data = item.date
    return render_template('edit_entries.html', form=form)

@app.route('/overview', methods=['GET'])
@login_required
def overview():
    presets = json_loader(True, "settings", "general")
    presets_loader = {}
    presets_loader['pagination'] = presets['pagination']
    currencies = presets['currencies']
    query_types = presets['currency_query']
    query_types.extend(currencies)
    presets_loader['currency_query'] = query_types
    presets_loader['currency_query_choice'] = current_user.setting('query currency')

    if True:                    #TODO #TODO #TODO #TODO

        last_query = dict(json.loads(current_user.setting('last_query')))
    # last_query={}

    return render_template('overview.html', title='test_main', presets_loader = presets_loader, last_query=last_query)



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




