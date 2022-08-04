import json

from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import Item, Price, UserSetting, User



class AjaxQuery():
    def __init__(self, requests):
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
                query = query.filter_by(name =  value)
            else:
                query = query.filter_by(category = value)

        query = query.join(Price)

        query_currency = current_user.setting('query currency')
        base_currency = current_user.setting('base currency')
        total = {}
        if query_currency == 'Total - base currency':
            query = query.filter_by(currency = base_currency)
            if query.count()>0:
                total[current_user.setting('base currency')] =  float(query.with_entities(func.sum(Price.price)).scalar())
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
        if hasattr(self, 'page'):
            query = query.offset(self.limit*(self.page-1))
        if hasattr(self, 'limit'):
            query = query.limit(self.limit)



        final={}
        rows = [x.to_dict(columns) for x in query.all()]
        final['columns'] = columns
        final['rows'] = rows
        final['count'] = count
        if hasattr(self, 'limit'):
            final['limit'] = self.limit
        if hasattr(self, 'page'):
            final['page'] = self.page

        total = [f"{k} = {v}" for k, v in total.items()]
        total = "TOTAL : " + " | ".join(total)
        final['total'] = str(total)



        if True:            #TODO edit later on
            saved = final.copy()
            for key in ['rows', 'columns', 'total']:
                if key in saved:
                    del saved[key]
            saved['time']=self.time
            # saved['query_type'] = self.query_type

            saved = json.dumps(saved)
            user = User.query.filter_by(id=current_user.id).first()
            setting = UserSetting.query.filter_by(setting_name='last_query').first()
            if setting is None:
                setting = UserSetting(setting_name='last_query', setting=saved)
                user.settings.append(setting)
            else:
                setting.setting = saved

            db.session.commit()

        return final


