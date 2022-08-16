import json
from flask import render_template, url_for, redirect, flash, request, render_template_string
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import union, except_
from sqlalchemy.orm import load_only
from app import app, db
from app.forms import LoginForm, RegistrationForm, ItemForm, ResetPasswordRequestForm, ResetPasswordForm, \
    EditUserPersonalForm, EditUserPasswordForm, EditUserSettingsForm
from app.email import send_password_reset_email
from app.models import User, Item, Category, Price, UserSetting
from app.utils.orms import AjaxQuery
from app.utils.helpers import currency_converter_api, json_loader, choice_list

from app import currency_converter_api, hipoteza


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
    property = requests['property']                                     # as to not hardcode the model name
    value = requests['value']
    test = Item.query.filter_by(user_id = current_user.id, name = value).first()
    aufofill_value = getattr(test, property, '')
    return {'data': str(aufofill_value)}

@app.route('/api/user-settings', methods=['POST'])
@login_required
def usersettings():
    requests = dict(json.loads(request.get_data()))
    setting_name = requests['setting_name']
    setting_value = requests['setting']
    setting = UserSetting.query.filter_by(user_id = current_user.id, setting_name = setting_name).first()
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
        user.set_setting('base_currency', form.currency.data)
        user.set_setting('query_currency', 'Total - base currency')
        user.set_setting('save_query', 'no')
        user.set_setting('temp_query', 'no')
        user.set_setting('last_query', '{}')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have successfuly registered your account')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
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
    return render_template('reset_password_request.html', title='Reset password', form=form)

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
    base_currency = current_user.setting('base_currency')
    choices = choice_list(base_currency, json_loader(True, "settings", "general", "currencies"))
    form = ItemForm()
    form.currency.choices = choices

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
            converted_price = currency_converter_api('EUR', base_currency, form.date.data, form.price.data)
            price2 = Price(
                price=converted_price,
                currency=base_currency,
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

@app.route('/<username>/items/<item>/<item_id>', methods=['GET', 'POST'])
@login_required
def item_edit(username, item, item_id):

    form = ItemForm()
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    price = Price.query.filter_by(item_id=item_id, first_entry=True).first()
    category = Category.query.filter_by(id=item.category_id).first()
    if request.method == 'POST':

        current_user.set_setting('temp_query', 'yes')
        db.session.commit()
        requested = (request.form.to_dict())
        if requested['submit'] == 'Cancel':

            return redirect(url_for('overview'))

        if requested['submit'] == 'Delete':
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
                    for prc in prices:
                        db.session.delete(prc)
                    price.price = form.price.data
                    price.currency = form.currency.data
                    base_currency = current_user.setting('base_currency')
                    if price.currency != base_currency:
                        # price_metadata={
                        #     {
                        #         'price': str(round(x[0], 2)),
                        #         'item_id': x[1],
                        #         'date': x[2].strftime('%Y-%m-%d'),
                        #         'base_currency': base_currency,
                        #         'comparison_currency': form.currency.data
                        #     }
                        #
                        #
                        # }

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
    presets_loader['currency_query_choice'] = current_user.setting('query_currency')

    if current_user.setting('temp_query')=='yes':
        last_query = current_user.setting('last_query')
    else:
        last_query = {}
    if current_user.setting('save_query') != 'yes':
        current_user.set_setting('temp_query', 'no')
        db.session.commit()
    return render_template('overview.html', title='test_main', presets_loader = presets_loader, last_query=last_query)

@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):                          #argument only for the URL, not used in the view function
    user = User.query.filter_by(username=current_user.username).first()
    if request.method == 'POST':
        requests = dict(json.loads(request.get_data()))
        submit_button = requests['submit']
        form_data = dict(json.loads(requests['data']))

        if submit_button == 'submit-personal':
            form = EditUserPersonalForm()
            form.username.data = form_data['username']
            form.email.data = form_data['email']
            form.csrf_token.data = form_data['csrf_token']
            if form.validate_on_submit():
                if user.username != form_data['username'] or user.email !=form_data['email']:
                    user.username = form_data['username']
                    user.email = form_data['email']
                    db.session.commit()
                    return {'data': ''}
                else:
                    return {'data': '-'}
            else:
                formErrors = render_template('forms/_edit_user_personal.html',form=form)
                return {'data': formErrors}
        if submit_button == 'submit-password':
            form = EditUserPasswordForm(current_user.username)
            form.old_password.data = form_data['old_password']
            form.password.data = form_data['password']
            form.password2.data = form_data['password2']
            form.csrf_token.data = form_data['csrf_token']
            if form.validate_on_submit():
                if user.check_password(password) != True:
                    db.session.commit()
                    return {'data': ''}
                else:
                    return {'data': '-'}
            else:
                formErrors = render_template('forms/_edit_user_password.html',form=form)
                return {'data': formErrors}
        if submit_button == 'submit-settings':
            form = EditUserSettingsForm()
            currencies = json_loader(True, "settings", "general", "currencies")
            form.currency.choices = choice_list(form_data['currency'], currencies)
            form.save_query.choices = ['yes', 'no']
            form.currency.data = form_data['currency']
            form.save_query.data = form_data['save_query']
            form.csrf_token.data = form_data['csrf_token']
            if form.validate_on_submit():
                if user.setting('save_query') != form.save_query.data or user.setting('base_currency') != form.currency.data:
                    if user.setting('save_query') != form.save_query.data:
                        user.set_setting('save_query', form.save_query.data)            #TODO could have sub-if-else
                    if user.setting('base_currency') != form.currency.data:
                        base_currency = user.setting('base_currency')

                        items = Item.query.filter(Item.user_id == 1)
                        items = items.join(Price)
                        items_pre = items.filter(Price.currency == user.setting('base_currency'))
                        items_post = items.filter(Price.currency == form.currency.data)
                        filtered_items = items_pre.except_(items_post).with_entities(Item.id).all()
                        items = db.session.query(Item, Price).outerjoin(Price, Item.id == Price.item_id).filter(Price.item_id.in_(([item[0] for item in filtered_items]))).filter(Price.currency=='RSD')

                        final = items.with_entities(Price.price, Item.id, Item.date).all()
                        final = [
                            {
                            'price': str(round(x[0], 2)),
                            'item_id': x[1],
                            'date': x[2].strftime('%Y-%m-%d'),
                            'base_currency': base_currency,
                            'comparison_currency': form.currency.data
                            }
                        for x in final]             #TODO

                        result = hipoteza(final)
                        user.set_setting('base_currency', form.currency.data)

                        # return {'data': str(result)}

                    db.session.commit()
                    return {'data': ''}
                else:
                    return {'data': '-'}
            else:
                flash('not confirmed')

                formErrors = render_template('forms/_edit_user_settings.html',form=form)
                return {'data': formErrors}

    return render_template('edit_profile.html', form=form)

@app.route('/api/edit-profile', methods=['POST'])
def edit_profile():
    requests = dict(json.loads(request.get_data()))
    value = requests['value']

    if value == 'Personal':
        form = EditUserPersonalForm()
        form.username.data = current_user.username
        form.email.data = current_user.email
        string = render_template('forms/_edit_user_personal.html', form=form)
        return {'data': string}

    if value == 'Password':
        form = EditUserPasswordForm(current_user.username)
        string = render_template('forms/_edit_user_password.html', form=form)
        return {'data': string}

    if value == 'Settings':
        form = EditUserSettingsForm(current_user.username)
        base_currency = current_user.setting('base_currency')
        currencies = json_loader(True, "settings", "general", "currencies")
        form.currency.choices = choice_list(base_currency, currencies)
        save_query = current_user.setting('save_query')
        form.save_query.choices = choice_list(save_query)
        string = render_template('forms/_edit_user_settings.html', form=form)
        return {'data': string}


