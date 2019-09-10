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
@app.route('/books')
def books():
    return render_template('books.html', items=mongo.db.items.find())
    
@app.route('/suggest')
def suggest():
    return 'Suggest A Book Page'

@app.route('/reading')
def reading():
    return 'Reading List Page'

@app.route('/complete')
def complete():
    return 'Complete A Book Page'

@app.route('/reviews')
def reviews():
    return 'Reviewed List Page'






if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)