import json
from flask import render_template, url_for, redirect, flash, request
from sqlalchemy.sql import except_              #TODO test if superfluous
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app import convert_prices
from app.forms import LoginForm, RegistrationForm, ItemForm, ResetPasswordRequestForm, ResetPasswordForm, \
    EditUserPersonalForm, EditUserPasswordForm, EditUserSettingsForm
from app.email import send_password_reset_email
from app.models import User, Item, Category, Price, UserSetting
from app.utils.orms import AjaxQuery
from app.utils.helpers import json_loader, choice_list

@app.route('/api/auto-suggest', methods=['POST'])
@login_required
def autosuggest():
    """
    Api route that receives the typed characters from an input field that is being monitored for input events,
    where on every keystroke an ajax request is sent to this route to check for the existing results matching
    the typed characters.
    User is queried as the one side of the relationship for either items or categories, on the many side of the
    respective relationship.
    """
    models = {'categories': Category, 'items': Item}

    request_data = dict(json.loads(request.get_data()))
    property = request_data['property']
    value = request_data['value']
    Model = models[property]        #db model can be either Item or Category, and a variable is defined here
                                    # in order not to hardcode two separate scenarios for the query
    query = Model.query.filter_by(user_id = current_user.id).filter(Model.name.ilike(f'{value}%')).with_entities(Model.name).distinct()
    results = [element.name for element in query]
    return {'data': results}

@app.route('/api/auto-fill', methods=['POST'])
@login_required
def autofill():
    """
    Api route that receives the name entered into an input field that is being monitored for the blur event,
    and if a condition is met for that name, i.e. there is a pair/relational value for it in the database,
    the function returns a referent value to fill another input field.
    Currently, it is used to check if the item/article name entered into the first field there has a predefined
    category set for it, and if so - the category name is returned and entered into the second input field.
    """
    request_data = dict(json.loads(request.get_data()))                     #TODO model dictionary at the beginning,
    property = request_data['property']                                     # as to not hardcode the model name
    value = request_data['value']
    query = Item.query.filter_by(user_id = current_user.id, name = value).first()
    aufofill_value = getattr(query, property, '')
    return {'data': str(aufofill_value)}

@app.route('/api/user-settings', methods=['POST'])
@login_required
def usersettings():
    """
    Api route that receives the name of a user setting and the new value for it, commits the change to the
    referent setting to the database, and returns back the value.
    Currently used only for the changes to the type of currency query - the ajax request gets sent on change
    event in the select field. This is the only query option that is considered a user setting, therefore
    it is necessary to commit the change to the database if the user opted for another type of query, assuming
    that the new choice will subsequently be used for multiple queries.
    """
    request_data = dict(json.loads(request.get_data()))
    setting_name = request_data['setting_name']
    setting_value = request_data['setting']
    setting = UserSetting.query.filter_by(user_id = current_user.id, setting_name = setting_name).first()
    setting.setting = setting_value
    db.session.add(setting)
    db.session.commit()
    return setting_value

@app.route('/api/tables', methods=['POST'])
@login_required
def tables():
    """
    Api route that receives the stringified JS object with all the query options chosen, which are then used in the
    AjaxQuery class to make a multi-step query, returning all the data which should be rendered/displayed back
    to the overview page.
    """
    request_data = dict(json.loads(request.get_data()))
    columns = ['item', 'category', 'price', 'date']     #list with attributes to be parsed from matching items in the
    query = AjaxQuery(request_data)                     # db - attributes are synonymous with table columns/column names
    query_results = query.querier(columns)
    return {'data': query_results}

@app.route('/api/edit-profile', methods=['POST'])
def edit_profile():
    """
    Api route that receives requests from the profile page, where the user can pick three different
    groups of personal settings to edit. Based on the chosen group, an ajax request is sent to this
    route, based on which the form for the requested settings is returned.
    This api route is used only for the first rendering of the form. In case the user submits the form
    and it does not get validated, the form gets returned from the profile page where the validation
    occurs - with the errors and info on what the user should change.
    The form gets rendered back as a string and gets reconstructed via innerHTML attribute of the
    form-container node - via javascript.
    """
    requests = dict(json.loads(request.get_data()))     #get the value of the clicked settings tab, based on which a
    value = requests['value']                           # relevant form is served back to the page

    if value == 'Personal':
        form = EditUserPersonalForm()
        form.username.data = current_user.username      #pre-populate the fields with existing data
        form.email.data = current_user.email
        string = render_template('forms/_edit_user_personal.html', form=form)
        return {'data': string}

    elif value == 'Password':
        form = EditUserPasswordForm(current_user.username)      #pre-populate the fields with existing data
        string = render_template('forms/_edit_user_password.html', form=form)
        return {'data': string}

    elif value == 'Settings':
        #re-organize the data for the two select fields - 'currency' and 'save queries'. The code
        # below uses the 'choice_list' function to pass the standard app options into the select field,
        # but place the previously chosen option by the user as the first one - i.e. active one
        form = EditUserSettingsForm()
        base_currency = current_user.setting('base_currency')
        currencies = json_loader(True, 'settings', 'general', 'currencies')
        form.currency.choices = choice_list(base_currency, currencies)
        save_query = current_user.setting('save_query')
        form.save_query.choices = choice_list(save_query)
        string = render_template('forms/_edit_user_settings.html', form=form)
        return {'data': string}

    else:
        pass #TODO - exception handling/raising errors

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    A view function handling the registration of new users.
    If the registration form is validated, this function also defines the standard user
    settings in the database in the UserSetting model (the many side of the relationship).
    These settings can then be changed subsequently if the user wishes to do so.
    Defining these settings at inception is important because they are actively used
    during the querying of results.
    """
    if current_user.is_authenticated:
        return render_template('entries.html', form=ItemForm())
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)     #create a new user instance
        user.set_setting('base_currency', form.currency.data)               #chosen currency taken from the form
        user.set_setting('query_currency', 'Total - base currency')         #other settings defined as neutral/standard,
        user.set_setting('save_query', 'no')                                # but also as placeholders in order to avoid
        user.set_setting('temp_query', 'yes')                               # 'NoneType' TypeError
        user.set_setting('last_query', '{}')                                #placeholder value until the first query is
        user.set_password(form.password.data)                               # made, preventing the 'NoneType' TypeError
        db.session.add(user)
        db.session.commit()
        flash('You have successfuly registered your account')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    A view function handling login and authentication of the users.
    Serves a login form, which if validated on submit, checks if the user exists and if the password is
    correct. On successful validation, it loads the 'entries' page as the landing page, so that the
    user instantly enter new expenses. If the login failed, the form is sent back to the user, with
    the relevant info on why the validation failed.
    """
    if current_user.is_authenticated:                                           #reroute if already logged in
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
    """
    A view function serving a password reset request form to the user - if the user forgot the password.
    The relevant user get queried by the single form entry which is the registered email, and if the user exists,
    an email with the link for resetting the password is sent to the registered email address for the user.
    """
    if current_user.is_authenticated:
        return redirect(url_for('/'))
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
    """
    A view function serving a password reset form to the user.
    The variable in the URL is the token used to authenticate the user, and the link the URL is received
    via the registered email. If the user is verified with the token, a password reset form is displayed,
    and if the form is validated - the new password is commited to the database.
    """
    if current_user.is_authenticated:
        return redirect(url_for('entries'))
    user = User.verify_reset_password_token(token)  #return the user if the token is valid
    if not user:
        return redirect(url_for('login'))           #redirect to login if the token is not valid
    form = ResetPasswordForm()
    if form.validate_on_submit():                   #if token was valid and the form was validated - change the password
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/entries', methods=['GET', 'POST'])
@login_required
def entries():
    """
    A view function that displays the form for entering new expenses.
    This is also the landing page for the logged in users, with the assumption that
    the entering of new expenses/data is a more common task than querying that data.
    """
    base_currency = current_user.setting('base_currency')   #get the default currency for the user
    choices = choice_list(base_currency, json_loader(True, 'settings', 'general', 'currencies'))    #load all currencies
    form = ItemForm()
    form.currency.choices = choices                         #pass pre-loaded currencies as options for the select field
                                                            # with the user's currency of choice as the first one
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

        #if the entered category exists, return it
        category = Category.query.filter_by(name=form.category.data, user_id=current_user.id).first()
        # if the entered category does not exist, create and commit it to the database
        if category is None:
            category = Category(
                name = form.category.data
            )
            current_user.categories.append(category)
        item.prices.append(price)
        category.items.append(item)
        current_user.items.append(item)

        #check if the items with the same name already exists and if their category matches the entered category,
        # and if the category does not match, it means that the category name was updated, in which case it is
        # necessary to update the category name for all the previously entered items of the same type
        sibling_items = Item.query.filter_by(name=form.item.data, user_id=current_user.id)
        if sibling_items.first().category != category.name:
            for item in sibling_items.all():
                item.category = category
                db.session.add(item)
        db.session.commit()

        #if the item price is not entered in the default/base currency for the user, the second price in the main   #TODO
        # currency also gets defined here, via a celery background task that sends an api request to a website
        # that returns that price converted to the default currency, with the exchange rate for the specified date
        #the celery function is used for looping over all the received results, and since in this case the request/
        # result is singular, it still needs to be placed inside a list because the for loop expects a list     #TODO
        currency = form.currency.data
        if currency != base_currency:
            item = Item.query.filter_by(category=form.category.data, user_id=current_user.id).all()[-1]
            price_metadata = [{
                'price': str(round(form.price.data, 2)),
                'item_id': item.id,
                'date': form.date.data.strftime('%Y-%m-%d'),
                'entry_currency': form.currency.data,
                'target_currency': base_currency,
                'first_entry': False
            }]
            convert_prices(price_metadata)

        return redirect(url_for('entries'))
    return render_template('entries.html', form=form)

@app.route('/<username>/items/<item>/<item_id>', methods=['GET', 'POST'])
@login_required
def item_edit(username, item, item_id):
    """
    A view function that displays the form for editing the existing expenses.
    The URL takes a couple of arguments, only one of which is used as a variable - to query
    the item and return the form, pre-populated with the existing data for the item.
    This page is accessed through the item links present in the table in the overview page -
    each link forming a unique view/URL for the item/articel in question.
    The submit buttons for this form differ from the form in the 'entries' view, where we have
    only the submit button. In this view function, user can confirm the edit, delete the item,
    or cancel the editing - all three options lead the user back to the overview page, with
    the most recent query (from which the user came to the item edit page via the item link)
    re-loaded.
    """


    #get the price/item/category data for the item, in order to pre-populate the form and subsequently
    # update the info for these db models in case the changes are made
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    price = Price.query.filter_by(item_id=item_id, first_entry=True).first()
    category = Category.query.filter_by(id=item.category_id).first()

    form = ItemForm()
    choices = choice_list(price.currency, json_loader(True, 'settings', 'general', 'currencies'))
    form.currency.choices = choices


    if request.method == 'POST':                    #if the user clicked any of the three submit buttons

        #change the temp_query setting for the user - necessary in order to re-display the most recent query when the
        # user gets rerouted back to the overview page, regardless of the setting that saves the most recent queries
        current_user.set_setting('temp_query', 'yes')
        db.session.commit()
        requested = (request.form.to_dict())
        if requested['submit'] == 'Cancel':         #if the user decided not to make changes - redirect to overview page
            return redirect(url_for('overview'))

        if requested['submit'] == 'Delete':         #delete the item from the database (cascaded price deletion)
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('overview'))

        elif requested['submit'] == 'Edit':         #submit changes to the item
            if form.validate_on_submit():
                #update the entry name and date if they were edited, i.e. if they differ from the pre-populated data
                if item.name != form.item.data or item.date != form.date.data:
                    item.name = form.item.data
                    item.date = form.date.data
                #update the category name if its name differs from the original category name for that item
                #if the newly named category already exists - get if from the db, and if it does not exist - create it
                if category.name != form.category.data:
                    category = Category.query.filter_by(
                        name=form.category.data,
                        user_id=current_user.id
                    ).first()
                    if category is None:
                        category = Category(
                            name=form.category.data
                        )
                    category.items.append(item)     #append the item to the category

                #if the price has been edited - get all the prices for the item (i.e. in all the currencies), delete
                # them, and then add the new price. If only the currency for that entry of the item in the database
                # is changed, the identical process is repeated - so that the 'first_entry' unique attribute for the
                # price gets removed from the database and the one with the new currency is added as 'first_entry'.
                # The 'first_entry' denotes that this one specific price is the original entry, and that all other
                # conversions of the price are derivatives - so that the user can track the original/correct currency
                # used for that expense.
                if price.price != form.price.data or price.currency != form.currency.data:
                    prices = Price.query.filter_by(item_id=item_id, first_entry=False).all()
                    for prc in prices:
                        db.session.delete(prc)
                    price.price = form.price.data
                    price.currency = form.currency.data
                    base_currency = current_user.setting('base_currency')

                    db.session.commit()         #TODO comment/explain
                    #if the currency for the entry differs from the default/base currency for that user, a conversions
                    # of the price is performed here, so that the user can query the price for that item both in
                    # the currency used for the purchase, as well as in the default currency
                    if price.currency != base_currency:

                        price_metadata= [{
                            'price': str(round(form.price.data, 2)),
                            'item_id': item_id,
                            'date': form.date.data.strftime('%Y-%m-%d'),
                            'entry_currency': form.currency.data,
                            'target_currency': base_currency,
                            'first_entry': True
                        }]

                        #conversion is done via a celery background task in order not to block the app - the task
                        # sends data to remote website with exchange rates and returns the converted price
                        convert_prices(price_metadata)


                return redirect(url_for('overview'))
    #at get request/first rendering of the page, pre-populate the form fields with existing data for that item.
    elif request.method == 'GET':
        form.item.data = item.name
        form.price.data = price.price
        form.currency.choice = price.currency
        form.category.data = item.category
        form.date.data = item.date
    return render_template('edit_entries.html', form=form)

@app.route('/overview', methods=['GET'])
@login_required
def overview():
    """
    A view function that displays calender widget with all the query options, allowing the user to query
    previous expenses entered into the database. Most of the functionalities are present on the page
    via JS scripts, which monitor what the user has clicked/chosen out of the query options, and they
    also handle the sending of ajax requests for the queries - where the ajax response serves back the data
    to the page, the data which is then used to create the table with the queried results.
    This function handles two elements which are sent to the page:

    1. Presets, in the form of 'preset_loader' variable, which contains app constants loaded from a
    JSON file - namely, the numbers of results per page, standard query options for the currencies and currency
    names. On top of that, it also retrieves the currency query type chosen by the user from the database - this is
    used to order/sort the currency query types in the select field, placing the chosen one as the first/active one.

    2. It goes through the user settings for 'temp_query' and 'save_query', and based on those values decides if the
    most recent query should be reconstructed and displayed when the user lands on the page. The 'temp_query' setting
    is used for the scenario where the user returns from the 'edit item' view, in which case it is always set to
    true (actually 'yes', as pseudo-boolean, since it is a user setting, and user settings are kept as strings), and
    false ('no') in all other cases. The 'save_query' is used as a 'global' setting - meaning that whenever the user
    lands on the overview page, the most recent query the user made is reconstructed and displayed.
    """

    if not current_user.is_authenticated:
        return render_template('login.html')

    presets = json_loader(True, 'settings', 'general')      #load all general settings/constants for the app
    currencies = presets['currencies']                      #load predefined currency names (3 at the moment)
    query_types = presets['currency_query']                 #load two more complex currency queries by generic name
    query_types.extend(currencies)                          #merge currency names with two queries above to form the
                                                            # total of 5 options for querying at the moment

    presets_loader = {}                         #new dictionary that holds the settings that are to be sent to the page
    presets_loader['pagination'] = presets['pagination']
    presets_loader['currency_query'] = query_types
    presets_loader['currency_query_choice'] = current_user.setting('query_currency')

    #if either of the settings is active/true - send the stringified JSON object back to the page to be used
    # to reconstruct and display the most recent query
    if current_user.setting('temp_query')=='yes' or current_user.setting('save_query')=='yes':
        last_query = current_user.setting('last_query')
    #else send an empty object, which when evaluated does not fork into the reconstructing of the most recent query TODO stringified? literate?
    else:
        last_query = '{}'
    #'save_query' option being active renders 'temp_query' option superfluous
    if current_user.setting('save_query') != 'yes':
        current_user.set_setting('temp_query', 'no')
        db.session.commit()
    return render_template('overview.html', title='test_main', presets_loader = presets_loader, last_query=json.loads(last_query))

@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):                          #argument only for the URL, not used in the view function
    """
    A view function allows the user to change multiple settings.
    The view presents an accordion type element with three groups of settings - personal (name, email), password, and
    settings (query-related settings - choice of basic/main currency, and if most recent queries are saved and
    displayed). Relevant forms for those three groups of settings get displayed via an ajax request (on click, with
    javascript handling that first display of the form), submission of the form is also handled via an ajax request,
    where the form data is sent in the body of the request. This was mostly done so that the three different forms can
    be parsed in the same route, instead of handling the similar logic and common elements in three different routes.
    Validation of the form data is done in this view function, and forms are served back to the page with error info
    if the validation failed - forms are sent as a html string in the body of the ajax response.
    Form data that is being submitted as an ajax request is imported here as a dictionary, and it lacks the validation
    functionalities that the WTForm classes have. For this reason, for the specific form a WTForm Class is instantiated
    and subsequently populated with the data received, so that it is possible to do the validation of that data by
    using WTForm functionalities. This allows the possibility to return back the form if it wasn't validated, and
    automatically have validation feedback for the user.
    """
    #user object handled via current_user instead of taking the variable from the URL - the variable practically serves
    # as a URL decorator/personalization
    user = User.query.filter_by(username=current_user.username).first()

    if request.method == 'POST':
        request_data = dict(json.loads(request.get_data()))
        submit_button = request_data['submit']
        form_data = dict(json.loads(request_data['data']))

        if submit_button == 'submit-personal':              #if the form for the personal settings was submitted
            form = EditUserPersonalForm()                   # instantiate the WTForm and populate it with the parsed
            form.username.data = form_data['username']      # data from the received form-content dictionary
            form.email.data = form_data['email']
            form.csrf_token.data = form_data['csrf_token']
            if form.validate_on_submit():                   #if form is validated
                #if there were changes made - return 'updated' string - used by JS as a conditional for flashing a
                # message to user; else - return 'no change' string, which is also used by JS as a conditional. Both of
                # these responses, apart from the flashed message, have the same effect - the form gets removed, and the
                # originally chosen tab/option gets 'unclicked', i.e. the 'chosen-option' css class is removed from it
                if user.username != form_data['username'] or user.email !=form_data['email']:
                    user.username = form_data['username']
                    user.email = form_data['email']
                    db.session.commit()
                    return {'data': 'updated'}
                else:
                    return {'data': 'no change'}
            # if from was not validated - return it back as an ajax response, now with info on what should be changed
            else:
                formErrors = render_template('forms/_edit_user_personal.html',form=form)
                return {'data': formErrors}

        if submit_button == 'submit-password':                      #if the form for changing the password was submitted
            form = EditUserPasswordForm(current_user.username)      #instantiate with current_user in order to be able
            form.old_password.data = form_data['old_password']      # to validate the old/current password
            form.password.data = form_data['password']
            form.password2.data = form_data['password2']
            form.csrf_token.data = form_data['csrf_token']
            if form.validate_on_submit():
                if user.check_password(password) != True:   #check if the user typed the old password as the new    #TODO
                    db.session.commit()                     # password... if not, commit the new password that was
                    return {'data': 'updated'}              # already validated (superfluous step)
                else:
                    return {'data': 'no change'}
            else:
                formErrors = render_template('forms/_edit_user_password.html',form=form)
                return {'data': formErrors}
        if submit_button == 'submit-settings':
            #if the form for changing the settings was submitted, populate the both select fields with the options to
            # choose from with standard values, but make the current user choice of those options the top/active one
            form = EditUserSettingsForm()
            currencies = json_loader(True, 'settings', 'general', 'currencies')
            form.currency.choices = choice_list(form_data['currency'], currencies)
            form.save_query.choices = ['yes', 'no']
            form.currency.data = form_data['currency']
            form.save_query.data = form_data['save_query']
            form.csrf_token.data = form_data['csrf_token']
            if form.validate_on_submit():
                #if any changes were made, check what those changes are with two sub-if clauses - and process them
                if user.setting('save_query') != form.save_query.data or user.setting('base_currency') != form.currency.data:
                    if user.setting('save_query') != form.save_query.data:
                        user.set_setting('save_query', form.save_query.data)  #update the setting for saving the queries

                    #if user changes the base/main currency, a complex query is made, with the goal to convert all the
                    # prices entered in the previous base/main currency into the new currency - while keeping the old
                    # prices as they are. This is done so that the user is able to query all the expenses ever made also
                    # in the newly chosen currency - which allows the user to always see total costs
                    if user.setting('base_currency') != form.currency.data:
                        #get the current base currency
                        base_currency = user.setting('base_currency')

                        #get all the items/expenses for the current user
                        items = Item.query.filter(Item.user_id == current_user.id)

                        #join Item model to Price model, in order to do further comparisons and filtering
                        items = items.join(Price)

                        #get all the items that have a price in the current (non-updated) base currency
                        items_pre = items.filter(Price.currency == user.setting('base_currency'))

                        #get all the items that have a price in the newly defined/changed base currency
                        items_post = items.filter(Price.currency == form.currency.data)

                        #get item IDs for all the items that would represent a difference between the two - so that no
                        # double-conversions are made into the new currency, if those prices already exist
                        filtered_items = items_pre.except_(items_post).with_entities(Item.id).all()

                        #use item IDs above to match those items with the prices - an outerjoin is performed,
                        # and the results are filtered in such a way that only the rows with the prices in the previous
                        # base/main currency are returned (since each item can have multiple prices/prices in multiple
                        # currencies). In this way, only the results containing Item+Price in the previous currency
                        # where there are no prices in the new currency are returned, in order to be parsed and sent for
                        # conversion to the new currency.
                        items = db.session.query(Item, Price)\
                            .outerjoin(Price, Item.id == Price.item_id)\
                            .filter(Price.item_id.in_(([item[0] for item in filtered_items])))\
                            .filter(Price.currency==base_currency)

                        #get the necessary info from the results for the api request to be made
                        final = items.with_entities(Price.price, Item.id, Item.date).all()

                        #form the dictionary with necessary arguments for the celery task that does conversion for the
                        # prices for n number of items
                        final = [{
                            'price': str(round(item[0], 2)),
                            'item_id': item[1],
                            'date': item[2].strftime('%Y-%m-%d'),
                            'entry_currency': base_currency,
                            'target_currency': form.currency.data,
                            'first_entry': False
                        } for item in final]

                        #start a celery task that uses a chord: it sends multiple API requests to a remote webpage,
                        # and only when all the results are returned (with converted prices) - the new data is
                        # entered into the database. The goal was to make a non-blocking background task, so that
                        # the app instantly renders back the profile page, if the user wants to make additional
                        # edits to any of the settings
                        convert_prices(final)       #only works if the celery worker is active
                        user.set_setting('base_currency', form.currency.data)
                    db.session.commit()
                    return {'data': 'updated'}
                else:
                    return {'data': 'no change'}
            else:
                formErrors = render_template('forms/_edit_user_settings.html',form=form)
                return {'data': formErrors}

    return render_template('edit_profile.html')




