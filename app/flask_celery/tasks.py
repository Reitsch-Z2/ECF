from celery import shared_task
from celery import signature, chord
from time import sleep


@shared_task(name='tester')
def tester(secs, package):
    sleep(secs)
    choiz = f'{secs}: {package}'
    return choiz


@shared_task(name='rezultati')
def rezultati(rez):

    return rez

@shared_task(name='hipoteza')
def hipoteza(results):
    chord(tester(2, str(x)) for x in results)(rezultati.s()).get()

@shared_task(name='currency_converter_api')
def currency_converter_api(price_metadata, base_currency, comparison_currency, date, quantity, decimals=2):
    url = f'https://api.exchangerate.host/convert?from={base_currency}&to={comparison_currency}'
    response = requests.get(url, {'amount': quantity, 'date': date})
    data = response.json()
    if 'result' in data:
        return round(data['result'], decimals)
    else :
        day_before = date - timedelta(days=1)
        yesterday = str(day_before)
        data = currency_converter_api(price_metadata, base_currency, comparison_currency, yesterday, quantity, decimals=2)
        return {'item_id': price_metadata['item_id'], 'currency':comparison_currency, 'price': data}