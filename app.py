from app import app, db
from app.models import User, Price, Item, Category, UserSetting

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', bind=True)

# @app.shell_context_processor
# def make_shell_context():
#     return {'db':db, 'User': User, 'Price': Price, 'Item': Item, 'Category': Category, 'UserSetting': UserSetting}