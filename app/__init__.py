from celery import signature, chord
from datetime import timedelta
import requests

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config.from_object(Config)
db=SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
mail = Mail(app)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)
from app.flask_celery.create_celery import create_celery
celery = create_celery(app)

#celery.autodiscover_tasks(['app.flask_celery'], force=True)
#from app.flask_celery.tasks import *

from app.models import Price
@celery.task(name='rezultati')
def rezultati(response):                #TODO optional/boolean for the commit to happen inside or outside the function?
    """
    A callback function for the header functions in a chord, used to perform database entries for the prices which were
    converted to another currency via an API request to a remote webpage that holds data on currency exchange rates.
    It waits for all the API responses with the new price/additional price data to return, and once all of them are
    ready, it loops through the data for each individual price and enters the prices into the database.
    It is used both for single-price conversions, where it is necessary to pass the price data as a dictionary within
    a list, but a more advanced usage is when the user changes the settings for the default currency. In the latter
    scenario, this function goes through all of the existing items for the user where the price in the newly defined
    main/base currency does not exist. After multiple API requests where sent and all the responses have been returned,
    this function populates the database with the additional prices in the new base currency based on the response data.
    This allows the user to retroactively make queries for total expenses in the newly defined base currency.
    """
    for item in response:
        price = Price(
            price=item['converted_price'],
            currency=item['target_currency'],
            item_id=item['item_id'],
            first_entry=item['first_entry']
        )

        db.session.add(price)
    db.session.commit()
    return response


@celery.task(name='convert_prices')
def convert_prices(results):
    """
    A chord task, with the header function that sends the API requests for price conversions to another currency, and
    the callback function that populates the database with new price entries based on the data received in the
    response(s) from the header function.
    """
    chord(currency_converter_api.s(x) for x in results)(rezultati.s())


@celery.task(name='currency_converter_api')
def currency_converter_api(price_data, decimals=2):
    """
    A function that makes an API request to a remote webpage that holds the historic data for the currency exchange
    rates. The function sends the data for the base and target currency, the relevant date, and the price for the base
    currency in the request, and parses only the newly defined price for the target currency from the response.
    It takes a dictionary as an argument, with all the data necessary for the new price to be entered into the database,
    it 'decorates'/appends the price in the target currency to the dictionary, and then returns the whole dictionary
    to the chord task, so that this data can be used to make a precise price entry into the database.
    """
    quantity = price_data['price']
    date = price_data['date']
    entry_currency = price_data['entry_currency']
    target_currency = price_data['target_currency']
    url = f'https://api.exchangerate.host/convert?from={entry_currency}&to={target_currency}'
    response = requests.get(url, {'amount': quantity, 'date': date})
    data = response.json()

    # If there is a result/new price in the response, add it to the dictionary that gets returned for the chord task
    if 'result' in data:
        price_data['converted_price'] = round(data['result'], decimals)
        return price_data

    # Else - in case the exchange rates for the current day are not yet defined on the relevant webpage, call the
    # function again with yesterday's date
    else :
        day_before = date - timedelta(days=1)
        yesterday = str(day_before)
        price_data['date'] = yesterday
        data = currency_converter_api(price_data, decimals=2)
        return data

    # TODO An alternative remote webpage as a "fallback", in case the primary one is not working

from app import routes

#https://ecf-expense-tracker.herokuapp.com/         //TODO





