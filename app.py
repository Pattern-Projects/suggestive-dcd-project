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
    return redirect( url_for('items') )     

@app.route('/delete/<item_id>')
def delete(item_id):
    items = mongo.db.items
    items.remove( {'_id':ObjectId(item_id)})
    return redirect(url_for( 'items' ))

@app.route('/favorite/<item_id>')
def favorite(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$push': {'favorites': 'John'}
    })
    return redirect(url_for( 'items' ) )   

@app.route('/unfavorite/<item_id>')
def unfavorite(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$pull': {'favorites': 'John'}
    })
    return redirect(url_for( 'items' ) )   

@app.route('/add_reading/<item_id>')
def add_reading(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {'reading': True}
    })
    return redirect(url_for( 'items' ) )

@app.route('/remove_reading/<item_id>')
def remove_reading(item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {'reading': False}
    })
    return redirect(url_for( 'items' ))

@app.route('/reading')
def reading():
    return render_template('reading.html', reading = mongo.db.items.find({'reading': True}))

@app.route('/add_current/<item_id>')
def add_current(item_id):
    items = mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {'status': 'current'}
    })
    return redirect(url_for( 'reading')) 

@app.route('/complete/<item_id>')
def complete(item_id):
    item =  mongo.db.items.find_one({"_id": ObjectId(item_id)})
    return render_template('complete.html', item=item) 

#Required - editing of data passed with POST

@app.route('/complete_item/<item_id>', methods=['POST'])
def complete_item(item_id):
    items = mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {
        'stars': request.form.get('stars'),
        'review': request.form.get('review'),
        'status': 'complete'
    }})
    return redirect( url_for( 'reviews') )     

@app.route('/reviews')
def reviews():
    return render_template('reviews.html', reviews = mongo.db.items.find({'status': 'complete'}))






if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)