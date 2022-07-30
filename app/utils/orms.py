from app.models import Item, Price
from flask_login import current_user




class AjaxQuery():
    def __init__(self, requests):
        self.requests_dict = requests['data']
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
        if query_currency == 'Total - base currency':
            query = query.filter_by(currency = base_currency)
        elif query_currency == 'Total - combined currencies':
            query = query.filter_by(first_entry = True)
        else:
            query = query.filter_by(currency = query_currency, first_entry = True)

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



        return final





# __name__ == "__main__":
#
#     currency_list_api('EUR', 'RSD', '2022-07-09', 200, 4)

    # x=json_loader(True, "settings", "general", "currencies")
    #
    # print(x)
