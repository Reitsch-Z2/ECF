from app.models import Item
from flask_login import current_user




class AjaxQuery():
    def __init__(self, requests):
        self.requests_dict = requests['data']
        self.time_mode = self.requests_dict['time']['mode']
        self.dates = self.requests_dict['time']['dates']
        # self.day = date_dict['day']
        # self.month = date_dict['month']
        # self.year = date_dict['year']

    # @staticmethod
    # def to_dict_mapper(itemlist, columnlist):
    #     return {'rows':[item.to_dict(columnlist) for item in itemlist], 'columns':columnlist}

    def querier(self, columns):
        query = Item.query.filter_by(user_id = current_user.id)

        if self.time_mode == 'day':
            query = query.filter(Item.date == self.dates)
        else:
            query = query.filter(Item.date.between(min(self.dates), max(self.dates)))




        final={}
        rows = [x.to_dict(columns) for x in query.all()]
        final['columns'] = columns
        final['rows'] = rows

        return final





# __name__ == "__main__":
#
#     currency_list_api('EUR', 'RSD', '2022-07-09', 200, 4)

    # x=json_loader(True, "settings", "general", "currencies")
    #
    # print(x)
