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

@app.route('/reading')
def reading():
    return render_template('reading.html')

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