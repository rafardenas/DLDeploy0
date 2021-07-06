import os 
import sys
#sys.path.append(os.getcwd())

from flask import render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
from flask_migrate import current 
from web_app.app import app, db
from web_app.app.forms import LoginForm, pred_form, RegistrationForm
from src import config
import torch
import transformers
from src.model import BERTBaseUncased
from flask_login import current_user, login_user, logout_user, login_required
from web_app.app.models import User 

# routes are defined with the following decorator
# in flask, the routes/links are defined with python functions
#we use the functions to send the information e.g. the inference
#then, we use the render_template function to decode it and present it with the filled placeholders

DEVICE = "cpu"
MODEL = BERTBaseUncased()
#MODEL.load_state_dict(torch.load(config.MODEL_PATH))  #loading the trained model
MODEL.to(DEVICE)
MODEL.eval()

#predictor function
def sentence_prediction(sentence):
    tokenizer = config.TOKENIZER
    max_len = config.MAX_LEN
    review = str(sentence)
    
    inputs = tokenizer.encode_plus(
    review, 
    None, 
    add_special_tokens=True,
    max_length=max_len,
    #pad_to_max_length=True
    padding='max_length',
    truncation=True
    )

    #print("Inputs", inputs)
    ids = inputs["input_ids"]
    mask = inputs["attention_mask"]
    token_type_ids = inputs["token_type_ids"]

    ids = torch.tensor(ids, dtype=torch.long).unsqueeze(0)
    mask =  torch.tensor(mask, dtype=torch.long).unsqueeze(0)
    token_type_ids = torch.tensor(token_type_ids, dtype=torch.long).unsqueeze(0)
    #print("shape with unsqueeze:", token_type_ids.shape)


    ids = ids.to(DEVICE,dtype=torch.long)
    mask = mask.to(DEVICE,dtype=torch.long)
    token_type_ids = token_type_ids.to(DEVICE,dtype=torch.long)

    outputs = MODEL(
        ids=ids, 
        mask=mask, 
        token_type_ids=token_type_ids
    )

    outputs = torch.sigmoid(outputs).cpu().detach().numpy()
    return outputs[0][0]


@app.route('/')
@app.route('/index')
@login_required
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
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        print('Next page argument is:', next_page)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    flash('Hello Anonymus')  
    return render_template('login.html', title='Sign In', form=form)
 


@app.route('/predict', methods = ['GET', 'POST'])
def predict():
    form = pred_form()
    if form.validate_on_submit():
        #print(form.sentence.data)
        inference = sentence_prediction(form.sentence.data)
        prediction = {
        "Query"    : form.sentence.data,
        "positive" : str(inference),
        "negative" : str(1 - inference)
        }
        return render_template('after.html', title='sentiment', data=prediction)
    else:
        return render_template('predict.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("User registered succesfully!")
        return redirect(url_for('login'))
    return render_template('register', title = "Signup", form=form)
    



