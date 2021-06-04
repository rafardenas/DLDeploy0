import os 
import sys
sys.path.append(os.getcwd())

from app import app
from flask import render_template

# routes are defined with the following decorator
# in flask, the routes/links are defined with python functions
#we use the functions to send the information e.g. the inference
#then, we use the render_template function to decode it and present it with the placeholders


@app.route('/')
@app.route('/index')
def index():
    user = {'username' : 'Rafael'}
    #have to send the elements as a list of dicts
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)



