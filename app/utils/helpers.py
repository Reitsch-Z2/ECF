import json
import os

def json_loader(path:bool or str, *args):
    """
    A function used to load the app-specific constants, such as currency types to choose from, typical numbers of
    results per page for the pagination element, as well as the names of two types of currency queries which are
    used to retrieve results in a specific manner (sum of all expenses for a certain period, either in default currency,
    or as a combination of currency specified the first time the item was entered).
    The constants are placed in a JSON file, which would probably get extended with other options in the future.
    """

    # if "True" is passed as the first argument, JSON is loaded from a predefined path
    if path == True:
        settings_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'settings', 'presets.json'))
    else:
        settings_path = os.path.normpath(path)      #alternatively, user can pass a custom path to JSON file
    with open(settings_path, "r") as config:
        sample_config = dict(json.load(config))
    for arg in args:                                #arguments passed are dict keys, each "nested" within the previous
        sample_config = sample_config[arg]          # one, leading to the target object/data deeper inside the JSON file
    return sample_config

def choice_list(choice, lista=['yes', 'no']):
    """
    A function used for reordering of data for select fields in html - it takes the "choice" argument, which is what
    the user has previously decided for out of predefined select options ("choices" often saved in user settings in
    the database), as well as all-options argument in the form of a list, and returns all-options with the user choice
    as the first element, so that is displayed properly in the select field (thus rendering the choice "active").
    If no list is passes as a second argument, one presumes that the choices to be made are yes/no, therefore the list
    with those two options is passed as default.
    """
    choices = lista[:]
    choices.remove(choice)
    return [choice, *choices]

#testing if the api request format is still correct, and if the remote webpage is active (fallback website planned)
if __name__ == '__main__':
    import requests
    result = currency_converter_api('RSD', 'EUR', '2022-07-09', 200, 4)
    print(result)

