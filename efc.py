from app import app, db
from app.models import User, Price, Item, Category

if __name__ == '__main__':
    app.run(debug=True, port=8080)

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User': User, 'Price': Price, 'Item': Item, 'Category': Category}