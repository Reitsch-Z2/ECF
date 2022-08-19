from celery import signature, chord
from time import sleep
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

# celery.autodiscover_tasks(['app.flask_celery'], force=True)
# from app.flask_celery.tasks import *



from app.models import Price
@celery.task(name='convert_prices')
def rezultati(response):
    for item in response:
        price = Price(
            price = item['converted_price'],
            currency = item['comparison_currency'],
            item_id = item['item_id'],
            first_entry = False
        )
        db.session.add(price)
    db.session.commit()
    return response

@celery.task(name='hipoteza')
def convert_prices(results):
    chord(currency_converter_api.s(x) for x in results)(rezultati.s())

@celery.task(name='currency_converter_api')
def currency_converter_api(price_metadata, decimals=2):
    id = price_metadata['item_id']
    quantity = price_metadata['price']
    date = price_metadata['date']
    base_currency = price_metadata['base_currency']
    comparison_currency = price_metadata['comparison_currency']
    url = f'https://api.exchangerate.host/convert?from={base_currency}&to={comparison_currency}'
    response = requests.get(url, {'amount': quantity, 'date': date})
    data = response.json()
    if 'result' in data:
        price_metadata['converted_price'] = round(data['result'], decimals)
        return price_metadata
    else :
        day_before = date - timedelta(days=1)
        yesterday = str(day_before)
        price_metadata['date'] = yesterday
        data = currency_converter_api(price_metadata, decimals=2)
        return data

from app import routes









