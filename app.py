import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/books')
def books():
    return 'Books List Page'

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