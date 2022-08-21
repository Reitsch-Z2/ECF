import json
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import Item, Price, UserSetting, User

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
    to make an identical query on return to the page, but continue at the same spot)
    """

    def __init__(self, requests):
        self.request = json.dumps(requests)
        self.requests_dict = requests['data']
        self.time = self.requests_dict['time']
        self.time_mode = self.requests_dict['time']['mode']
        self.dates = self.requests_dict['time']['dates']
        self.pagination = self.requests_dict['pagination']
        if 'limit' in self.pagination:
            self.limit = int(self.pagination['limit'])
        if 'page' in self.pagination:
            self.page = int(self.pagination['page'])
        if bool(self.requests_dict['query_type']):
            self.query_type = self.requests_dict['query_type']

    def querier(self, columns):
        query = Item.query.filter_by(user_id = current_user.id)
        if self.time_mode == 'day':
            query = query.filter(Item.date == self.dates)
        else:
            query = query.filter(Item.date.between(min(self.dates), max(self.dates)))

        if hasattr(self, 'query_type'):
            (type, value), = self.query_type.items()
            if type == 'Item':
                query = query.filter_by(name = value)
            else:
                query = query.filter_by(category = value)

        query = query.join(Price)
        query_currency = current_user.setting('query_currency')
        base_currency = current_user.setting('base_currency')
        total = {}
        final = {}

        if query_currency == 'Total - base currency':
            query = query.filter_by(currency = base_currency)
            if query.count()>0:
                total[current_user.setting('base_currency')] = float(query.with_entities(func.sum(Price.price)).scalar())
        elif query_currency == 'Total - combined currencies':
            query = query.filter_by(first_entry = True)
            if query.count() > 0:
                currencies = query.with_entities(Price.currency).distinct()
                for currency in currencies:
                    currency = currency[0]
                    total[currency]=float(query.filter(Price.currency==currency).with_entities(func.sum(Price.price)).scalar())
        else:
            query = query.filter_by(currency = query_currency, first_entry = True)
            if query.count() > 0:
                total[query_currency] = float(query.with_entities(func.sum(Price.price)).scalar())

        count = query.count()

        if count == 0:          #short-circuit the response if there are no query results
            return {}

        query = query.offset(self.limit*(self.page-1))
        query = query.limit(self.limit)
        rows = [x.to_dict(columns) for x in query.all()]
        total = [f"{k} = {v}" for k, v in total.items()]
        total = "TOTAL : " + " | ".join(total)

        final['columns'] = columns          #final dict contains query option data + additional elements such as sum and
        final['rows'] = rows                # count, which are to be rendered on the page. In addition to those, it
        final['count'] = count              # contains/returns the active query back to the page, so that if the user
        final['limit'] = self.limit         # navigates to the edit item page, the query could be reloaded when the user
        final['page'] = self.page           # gets redirected back to the overview page
        final['total'] = str(total)
        final['saved'] = self.request

        if current_user.setting('save_query') == 'yes':
            setting = UserSetting.query.filter_by(user_id= current_user.id, setting_name='last_query').first()
            if setting is None:
                setting = UserSetting(setting_name='last_query', setting=self.request)
                user.settings.append(setting)
            else:
                setting.setting = self.request
            db.session.commit()

        return final


