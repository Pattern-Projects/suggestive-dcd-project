import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def test():
    return 'Ello world'

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT', 8000)),
            debug=True)