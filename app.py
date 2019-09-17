import os
from flask import Flask, session, render_template, redirect, escape, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib

app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = 'dfa#3jfDl7j?sl'
DBS_NAME = "suggestive"
COLLECTION_NAME = "itmes"
mongo = PyMongo(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', users=mongo.db.users.find())

@app.route('/myinfo')
def myinfo():
    if session.get('username'):
        list_profile = session['username']
        return render_template('info.html', list_profile = list_profile)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        found = False
        
        dbusers = mongo.db.users.find({'username': username})
        for user in dbusers:
            found = True
            if user['password'] == password:
                session['username'] = user['username']
                return redirect(url_for('myinfo'))
            else:
                return render_template('login.html', mismatch=True)
                
        if found == False:
            users =  mongo.db.users
            user = request.form.to_dict()
            user['password'] = password
            users.insert_one(user)
            session['username'] = username
            return redirect(url_for('home'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/list/<list_profile>')
def open(list_profile):
    if list_profile:
        return render_template('info.html', list_profile = list_profile)
    return render_template('home.html')


@app.route('/info/<list_profile>')
def info(list_profile):
    if list_profile:
        return render_template('info.html', list_profile = list_profile)
    return render_template('home.html')
    
@app.route('/items/<list_profile>')
def items(list_profile):
    return render_template('items.html', list_profile = list_profile, items=mongo.db.items.find({'owner': list_profile,  'status': { '$in': [ 'suggested', 'reading' ] } }))
    
@app.route('/suggest/<list_profile>')
def suggest(list_profile):
    if session.get('username'):
        return render_template('suggest.html',
                                authors=mongo.db.authors.find(), list_profile = list_profile)
    else:
        return render_template('login.html')

@app.route('/insert_item/<list_profile>', methods=['POST'])
def insert_item(list_profile):
    if session.get('username'):

        items =  mongo.db.items
        item = request.form.to_dict()
        item['favorites'] = []
        item['status'] = 'suggested'
        item['owner'] = list_profile
        item['suggester'] = session['username']
        items.insert_one(item)
        
    return redirect( url_for('items', list_profile = list_profile ))     

@app.route('/delete/<list_profile>/<page>/<item_id>')
def delete(list_profile, page, item_id):
    if session.get('username'):
        items = mongo.db.items.find({'_id':ObjectId(item_id)})
        for item in items:
            if item['owner'] == session['username'] or item['suggester'] == session['username']:
                mongo.db.items.remove( {'_id':ObjectId(item_id)})
    return redirect(url_for( page, list_profile = list_profile ))

@app.route('/favorite/<list_profile>/<page>/<item_id>')
def favorite(list_profile, page, item_id):
    if session.get('username'):
        items =  mongo.db.items
        if 'username' in session:
            items.update( {'_id': ObjectId(item_id)},
            {
                '$push': {'favorites': session['username']}
            })
    return redirect(url_for( page, list_profile = list_profile ) )   

@app.route('/unfavorite/<list_profile>/<page>/<item_id>')
def unfavorite(list_profile, page, item_id):
    if session.get('username'):
        items =  mongo.db.items
        if 'username' in session:
            items.update( {'_id': ObjectId(item_id)},
            {
                '$pull': {'favorites': session['username']}
            })
    return redirect(url_for( page, list_profile = list_profile ) )   

@app.route('/set_status/<list_profile>/<page>/<status>/<item_id>')
def set_status(list_profile, page, status, item_id):
    if session.get('username'):
        items = mongo.db.items.find({'_id':ObjectId(item_id)})
        for item in items:
            if item['owner'] == session['username']:
                mongo.db.items.update( {'_id': ObjectId(item_id)},
                {
                    '$set': {'status': status }
                })
    return redirect(url_for( page, list_profile = list_profile ) )

@app.route('/reading/<list_profile>')
def reading(list_profile):
    return render_template('reading.html', list_profile = list_profile, reading = mongo.db.items.find({'owner': list_profile, 'status': { '$in': [ 'reading', 'current' ] } }))

@app.route('/complete/<list_profile><item_id>')
def complete(list_profile, item_id):
    if session.get('username'):
        item =  mongo.db.items.find_one({"_id": ObjectId(item_id)})
        return render_template('complete.html', item=item) 
    return render_template('reading.html', list_profile = list_profile)
    
#Required - editing of data passed with POST

@app.route('/complete_item/<list_profile>/<item_id>', methods=['POST'])
def complete_item(list_profile, item_id):
    if session.get('username'):
        items = mongo.db.items.find({'_id':ObjectId(item_id)})
        for item in items:
            if item['owner'] == session['username']:    
                mongo.db.items.update( {'_id': ObjectId(item_id)},
                {
                    '$set': {
                    'stars': request.form.get('stars'),
                    'review': request.form.get('review'),
                    'status': 'complete',
                    'complete': True
                }})
    return redirect( url_for( 'reviews', list_profile = list_profile) )     

@app.route('/reviews/<list_profile>')
def reviews(list_profile):
    return render_template('reviews.html', list_profile = list_profile, reviews = mongo.db.items.find({'owner': list_profile, 'complete': True}))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)