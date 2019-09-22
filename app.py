# <Suggestive - A book suggestion tool geared toward social media content creators with a medium to large fanbase.>
#   Copyright (C) <2019>  <John O' Sullivan>

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>. 


import os
from flask import Flask, session, render_template, redirect, escape, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import hashlib
import cProfile
import re

app = Flask(__name__)

# environment variables
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv("MONGO_URI")

# inti pymongo
mongo = PyMongo(app)


# Home, Login, Logout

# Home page - from home button
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', users=mongo.db.users.find({'public': 'on'}))

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if theres info in post
    if request.method == 'POST':
        
        # extract data from post
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        found = False
        
        # Look for users with these details
        dbusers = mongo.db.users.find({'username': username})
        for user in dbusers:
            # That username was found
            found = True
            if user['password'] == password:
                # Passwords matched
                session['username'] = user['username']
                return redirect(url_for('myinfo'))
            else:
                # Passwords didn't match - back to login with warning
                return render_template('login.html', mismatch=True)

        # username not found - one created and logged in
        if found == False:
            users =  mongo.db.users
            user = request.form.to_dict()
            user['password'] = password
            user['public'] = 'off'
            users.insert_one(user)
            session['username'] = username
            return redirect(url_for('home'))
        
    return render_template('login.html')

# Log out and redirect to home
@app.route('/logout')
def logout():
    # remove the username from the session
    session.pop('username', None)
    return redirect(url_for('home'))


# Users

# My Info Page
@app.route('/myinfo')
def myinfo():
    # if the user is signed in
    if 'username' in session:
        # Render users info page
        list_profile = session['username']
        suggested = mongo.db.items.count_documents({'owner': list_profile})
        complete = mongo.db.items.count_documents({'owner': list_profile, 'complete':True})        
        return render_template('info.html',suggested=suggested, complete=complete, list_profile = list_profile, profiles=mongo.db.users.find({'username':list_profile}))
    # Else redirect to lgin page
    return redirect(url_for('login'))

# Open info page for given user
@app.route('/info/<list_profile>')
def info(list_profile):
    if list_profile:
        # Retrieve info for user table
        suggested = mongo.db.items.count_documents({'owner': list_profile})
        complete = mongo.db.items.count_documents({'owner': list_profile, 'complete':True})

        # Render page
        return render_template('info.html',suggested=suggested, complete=complete, list_profile = list_profile, profiles=mongo.db.users.find({'username':list_profile}))
    # otehrwise return to home page
    return render_template('home.html')
    
# Update the users list information - including their blurb and whether their list is public
@app.route('/update_info/<list_profile>', methods=['POST'])
def update_info(list_profile):
    # If a user is logged in
    if 'username' in session:
        item = request.form.to_dict()
        blurb = item['blurb']
        # set list to public if switch is on
        if item.get('public'):
            public = 'on'
        else:
            public = 'off'

        users =  mongo.db.users.find({'username': list_profile})
        for user in users:
            if user['username'] == session['username']:
                mongo.db.users.update( {'_id': ObjectId(user['_id'])},
                {
                    '$set': {'blurb': blurb, 'public' : public }
                })
    return redirect( url_for('info', list_profile = list_profile ))     

# Delete user
@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    # Ensure a user is logged in
    if 'username' in session:
        users = mongo.db.users.find({'_id':ObjectId(user_id)})
        for user in users:
        # Ensure it is correct user
            if user['username'] == session['username']:
                mongo.db.users.remove( {'_id':ObjectId(user_id)})
                mongo.db.items.remove( {'owner': user['username']})
    # Log out deleted user
    return redirect(url_for('logout'))


# Pages - Suggested, Reading, Reviews

# Open the Suggested books page page
@app.route('/items/<list_profile>')
def items(list_profile):
    return render_template('items.html',profiles=mongo.db.users.find({'username':list_profile}), list_profile = list_profile, items=mongo.db.items.find({'owner': list_profile,  'status': { '$in': [ 'suggested', 'reading' ] } }).sort([('favorites_count',-1)]))

# Open reading list page
@app.route('/reading/<list_profile>')
def reading(list_profile):
    return render_template('reading.html', list_profile = list_profile, reading = mongo.db.items.find({'owner': list_profile, 'status': { '$in': [ 'reading', 'current' ] } }).sort([('favorites_count',-1)]))

# Open reviews page
@app.route('/reviews/<list_profile>')
def reviews(list_profile):
    return render_template('reviews.html', list_profile = list_profile, reviews = mongo.db.items.find({'owner': list_profile, 'complete': True}).sort([('favorites_count',-1)]))

# Books - Insert, Update, Delete

# Render the suggest a book page    
@app.route('/suggest/<list_profile>')
def suggest(list_profile):
    if 'username' in session:
        return render_template('suggest.html',
                                profiles=mongo.db.users.find({'username':list_profile}), list_profile = list_profile)
    else:
        return render_template('login.html')

# Insert a suggested book
@app.route('/insert_item/<list_profile>', methods=['POST'])
def insert_item(list_profile):
    # If a user is logged in
    if 'username' in session:
        # Massage data and insert
        items =  mongo.db.items
        item = request.form.to_dict()
        item['favorites'] = []
        item['status'] = 'suggested'
        item['owner'] = list_profile
        item['suggester'] = session['username']
        items.insert_one(item)
        
    return redirect( url_for('items', list_profile = list_profile ))     

# Open the complete a book page
@app.route('/complete/<list_profile>/<item_id>')
def complete(list_profile, item_id):
    # If a user is logged in
    if 'username' in session:
        item =  mongo.db.items.find_one({"_id": ObjectId(item_id)})
        return render_template('complete.html', list_profile = list_profile, item=item) 
    return render_template('reading.html', list_profile = list_profile)
    
# Complete a book - add a star rating and a review
@app.route('/complete_item/<list_profile>/<item_id>', methods=['POST'])
def complete_item(list_profile, item_id):
    # If a user is signed in
    if 'username' in session:
        items = mongo.db.items.find({'_id':ObjectId(item_id)})
        for item in items:
            # If signed in user is the owner of the book
            if item['owner'] == session['username']:    
                mongo.db.items.update( {'_id': ObjectId(item_id)},
                {
                    '$set': {
                    'stars': int(request.form.get('stars')),
                    'review': request.form.get('review'),
                    'status': 'complete',
                    'complete': True
                }})
    return redirect( url_for( 'reviews', list_profile = list_profile) )     


# Add a favorite to the book
@app.route('/favorite/<list_profile>/<page>/<item_id>')
def favorite(list_profile, page, item_id):
    # If a user is logged in
    if 'username' in session:
        items =  mongo.db.items
        items.update( {'_id': ObjectId(item_id)},
        {
            '$push': {'favorites': session['username']},
                 '$inc': { 'favorites_count': 1 }
            
        })
            
        return redirect(url_for( page, list_profile = list_profile ) )
    return render_template('login.html')

# Remove a favorite from the book
@app.route('/unfavorite/<list_profile>/<page>/<item_id>')
def unfavorite(list_profile, page, item_id):
    if 'username' in session:
        items =  mongo.db.items
        items.update( {'_id': ObjectId(item_id)},
        {
            '$pull': {'favorites': session['username']},
                 '$inc': { 'favorites_count': -1 }
            
        })
        return redirect(url_for( page, list_profile = list_profile ) )   
    return render_template('login.html')

# Update the status of the book - dictates which page it will appear on
@app.route('/set_status/<list_profile>/<page>/<status>/<item_id>')
def set_status(list_profile, page, status, item_id):
    # If a user is logged in
    if 'username' in session:
        items = mongo.db.items.find({'_id':ObjectId(item_id)})
        for item in items:
            # If the logged in user is the owner of the book
            if item['owner'] == session['username']:

                mongo.db.items.update( {'_id': ObjectId(item_id)},
                {
                    '$set': {'status': status }
                })
        return redirect(url_for( page, list_profile = list_profile ) )
    return render_template('login.html')

# Delete book
@app.route('/delete/<list_profile>/<page>/<item_id>')
def delete(list_profile, page, item_id):
    # If a user is logged in
    if 'username' in session:
        items = mongo.db.items.find({'_id':ObjectId(item_id)})
        for item in items:
            # if the user is the owner of the list or the suggestor of the book
            if item['owner'] == session['username'] or item['suggester'] == session['username']:
                mongo.db.items.remove( {'_id':ObjectId(item_id)})
    return redirect(url_for( page, list_profile = list_profile ))

# Run the app
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)