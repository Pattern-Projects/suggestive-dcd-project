import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
DBS_NAME = "suggestive"
COLLECTION_NAME = "itmes"

mongo = PyMongo(app)

@app.route('/')
@app.route('/items')
def items():
    return render_template('items.html', items=mongo.db.items.find())
    
@app.route('/suggest')
def suggest():
    return render_template('suggest.html',
                                authors=mongo.db.authors.find())

@app.route('/insert_item', methods=['POST'])
def insert_item():
    items =  mongo.db.items
    items.insert_one(request.form.to_dict())
    return redirect( url_for('items') )     #not working?

@app.route('/favorite/<item_id>')
def favorite(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$push': {'favorites': 'John'}
    })
    return redirect(url_for( 'items' ) )   #not working?

@app.route('/unfavorite/<item_id>')
def unfavorite(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$pull': {'favorites': 'John'}
    })
    return redirect(url_for( 'items' ) )   #not working?

@app.route('/add_reading/<item_id>')
def add_reading(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {'reading': True}
    })
    return redirect(url_for( 'items' ) )   #not working?

@app.route('/remove_reading/<item_id>')
def remove_reading(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {'reading': False}
    })
    return redirect(url_for( 'items' ))   #not working?

@app.route('/reading')
def reading():
    return render_template('reading.html', reading = mongo.db.items.find({'reading': True}))

@app.route('/add_current/<item_id>')
def add_current(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {'status': 'current'}
    })
    return redirect(url_for( 'reading'))   #not working?

@app.route('/complete')
def complete():
    return 'Complete A Book Page'

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')






if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)