import json
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import Item, Price, UserSetting

class AjaxQuery():
    """
    Class used to process the ajax query and return the results based on options chosen.
    It returns multiple elements as a response, all of which are displayed in different
    elements on the overview page:
        - Query results for the expenses
        - Current page for the pagination
        - Sum of all queried expenses, based on the type of currency query
    On top of that, if the user has chosen to save/remember the last query, the last query
    is committed to the database and gets displayed the next time the user goes to the overview
    page. If the option is not selected, the class instance still returns the last query,
    so that the user who edits the item/article data can return back to the overview page with
    the active query after the editing of an item has been done (so that the user does not have
    to make an identical query on return to the page, but continue at the same spot, with the
    query reloaded)
    """
    def __init__(self, requests):                       # Parsing the data from the object received in the request body
        self.request = json.dumps(requests)
        self.requests_dict = requests['data']
        self.time = self.requests_dict['time']
        self.time_mode = self.requests_dict['time']['mode']
        self.dates = self.requests_dict['time']['dates']
        self.pagination = self.requests_dict['pagination']
        self.limit = int(self.pagination['limit'])
        self.page = int(self.pagination['page'])
        if bool(self.requests_dict['query_type']):      # The only query "optional" option - check if it was chosen
            self.query_type = self.requests_dict['query_type']

    def querier(self, columns: list):
        """
        The main (and only) method of the class, used to query the database based on the parameters
        received in the request body. There are multiple levels of querying - the query parameters/options
        practically get chained onto one another, in order to get final results to be served back to the page.
        """
        query = Item.query.filter_by(user_id=current_user.id)   # Limit the access to data for the authenticated user


        if self.time_mode == 'day':                             # If querying in "day" mode, filter by a single date
            query = query.filter(Item.date == self.dates)       # Else - if querying in week/month mode, use the first
        else:                                                   # and last day of the week/month to filter the results
            query = query.filter(Item.date.between(min(self.dates), max(self.dates)))

        if hasattr(self, 'query_type'):                         # Filter the results by item/category name, if the user
            (type, value), = self.query_type.items()            # decided to go with that option
            if type == 'Item':
                query = query.filter_by(name=value)
            else:
                query = query.filter_by(category=value)

        query = query.join(Price)                                   # Join with the Price model for further filtering
        query_currency = current_user.setting('query_currency')     # based on the currency results the user wants
        base_currency = current_user.setting('base_currency')
        total = {}
        final = {}

        # Get all the results in the default currency
        if query_currency == 'Total - base currency':
            query = query.filter_by(currency=base_currency)
            if query.count()>0:
                total[current_user.setting('base_currency')] = float(query.with_entities(func.sum(Price.price)).scalar())

        # Get all the results in the currency chosen at first entry
        elif query_currency == 'Total - combined currencies':
            query = query.filter_by(first_entry=True)
            if query.count() > 0:
                currencies = query.with_entities(Price.currency).distinct()
                for currency in currencies:
                    currency = currency[0]
                    total[currency]=float(query.filter(Price.currency==currency).
                        with_entities(func.sum(Price.price)).scalar())

        # Get all the results for a currency where the first entry into the database was made with that
        # currency, i.e. if the user made a query for a singular currency, only the results where the
        # original price is in that currency are returned
        else:
            query = query.filter_by(currency=query_currency, first_entry=True)
            if query.count() > 0:
                total[query_currency] = float(query.with_entities(func.sum(Price.price)).scalar())

        count = query.count()                               # Check the number of results after the filtering
        if count == 0:                                      # Short-circuit the response if there are no query results
            return {}

        query = query.offset(self.limit*(self.page-1))      # Enforce limit and offset on the query, so that only the
        query = query.limit(self.limit)                     # partial results (in sync with pagination parameters) are
        rows = [x.to_dict(columns) for x in query.all()]    # returned
        total = [f'{k} = {v}' for k, v in total.items()]    # Format and return the sum of all expenses in a string form
        total = "TOTAL : " + " | ".join(total)              # to be displayed underneath the table with results

        final['columns'] = columns          # Final dict contains query options data + additional elements such as sum
        final['rows'] = rows                # and count, which are to be rendered on the page. In addition to those, it
        final['count'] = count              # contains/returns the active query back to the page, so that if the user
        final['limit'] = self.limit         # navigates to the edit item page, the query could be reloaded when the user
        final['page'] = self.page           # gets redirected back to the overview page
        final['total'] = str(total)

        # If the user chose to save the most recent query, the request object is committed to the db as a stringified
        # JSON object, and then used to reload the query when the user goes back to the overview page
        if current_user.setting('save_query') == 'yes':
            setting = UserSetting.query.filter_by(user_id=current_user.id, setting_name='last_query').first()
            if setting is None:
                setting = UserSetting(setting_name='last_query', setting=self.request)
                user.settings.append(setting)
            else:
                setting.setting = self.request
            db.session.commit()

        return final


