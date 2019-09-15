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
    
    item = request.form.to_dict()
    item['favorites'] = []
    
    items.insert_one(item)
    
    return redirect( url_for('items') )     

@app.route('/delete/<page>/<item_id>')
def delete(page, item_id):
    items = mongo.db.items
    items.remove( {'_id':ObjectId(item_id)})
    return redirect(url_for( page ))

@app.route('/favorite/<page>/<item_id>')
def favorite(page, item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$push': {'favorites': 'John'}
    })
    return redirect(url_for( page ) )   

@app.route('/unfavorite/<page>/<item_id>')
def unfavorite(page, item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$pull': {'favorites': 'John'}
    })
    return redirect(url_for( page ) )   

@app.route('/set_status/<page>/<status>/<item_id>')
def set_status(page, status, item_id):
    items =  mongo.db.items
    items.update( {'_id': ObjectId(item_id)},
    {
        '$set': {'status': status }
    })
    return redirect(url_for( page ) )

@app.route('/reading')
def reading():
    return render_template('reading.html', reading = mongo.db.items.find({ 'status': { '$in': [ 'reading', 'current' ] } }))

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
        'status': 'complete',
        'complete': True
    }})
    return redirect( url_for( 'reviews') )     

@app.route('/reviews')
def reviews():
    return render_template('reviews.html', reviews = mongo.db.items.find({'complete': True}))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)