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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        found = False
        
        dbusers = mongo.db.users.find({'username': username})
        print('num', dbusers.count)
        for user in dbusers:
            found = True
            if user['password'] == password:
                print ('username and password match')
                session['username'] = user['username']
            else:
                print ('password doesnt match')
                return 'The username exists already with a different password'
                
        if found == False:
            print ('username doesnt match')
            users =  mongo.db.users
            user = request.form.to_dict()
            user['password'] = password
            users.insert_one(user)
            session['username'] = username
                
        # ===============
        
        # Find users in mongo
        # matchedusers = mongo.db.users.find({'username': username})
        
        # for user in matchedusers:
        #     if user['password'] == password:  #Bug: hash is randomised
        #         session['username'] = request.form['username']
        #         # session['id'] = user['_id']
        #         found = True
                
        # if found is False:
        #     users =  mongo.db.users
        #     user = request.form.to_dict()
        #     user['password'] = password
        #     users.insert_one(user)  #bug: retrieve _id of inserted user
        #     session['username'] = request.form['username']
            # session['id'] = id    #Fix: _id of inseted user
            # create
        
        print(request.form['password'], password)
        return redirect(url_for('items'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('items'))

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
    if 'username' in session:
        items.update( {'_id': ObjectId(item_id)},
        {
            '$push': {'favorites': session['username']}
        })
    return redirect(url_for( page ) )   

@app.route('/unfavorite/<page>/<item_id>')
def unfavorite(page, item_id):
    items =  mongo.db.items
    if 'username' in session:
        items.update( {'_id': ObjectId(item_id)},
        {
            '$pull': {'favorites': session['username']}
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