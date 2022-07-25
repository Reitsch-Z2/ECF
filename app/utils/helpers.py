import json
import os
import requests
from app.models import Item



def json_loader(path:bool or str, *args):               #TODO can we do this?
    if path == True:
        settings_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "settings", "presets.json"))
    else:
        settings_path = os.path.normpath(os.path.join(os.path.dirname(__file__), path))
    with open(settings_path, "r") as config:
        sample_config = dict(json.load(config))

    for arg in args:
        sample_config = sample_config[arg]

    return sample_config


def currency_converter_api(base_currency, comparison_currency, date, quantity, decimals=2):

    url = f'https://api.exchangerate.host/convert?from={base_currency}&to={comparison_currency}'
    response = requests.get(url, {'amount': quantity, 'date': date})
    data = response.json()
    data = round(data['result'], decimals)

    return data

if __name__ == "__main__":

    currency_list_api('EUR', 'RSD', '2022-07-09', 200, 4)


    # '07/25/2022'
    # x=json_loader(True, "settings", "general", "currencies")
    #
    # print(x)
