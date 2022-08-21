import json
import os

def json_loader(path:bool or str, *args):               #TODO can we do this?
    if path == True:
        settings_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'settings', 'presets.json'))
    else:
        settings_path = os.path.normpath(os.path.join(os.path.dirname(__file__), path))
    with open(settings_path, "r") as config:
        sample_config = dict(json.load(config))
    for arg in args:
        sample_config = sample_config[arg]
    return sample_config

def choice_list(choice, lista=['yes', 'no']):
    choices = lista[:]
    choices.remove(choice)
    return [choice, *choices]

if __name__ == '__main__':
    x = currency_converter_api('EUR', 'RSD', '2022-07-09', 200, 4)
    print(x)

