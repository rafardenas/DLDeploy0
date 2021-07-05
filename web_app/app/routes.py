import os 
import sys
#sys.path.append(os.getcwd())

from flask import render_template, flash, redirect, url_for 
from web_app.app import app
from web_app.app.forms import LoginForm, pred_form
from src import config
import torch
import transformers
from src.model import BERTBaseUncased

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
    return render_template('index.html', title=None, user=user, posts=posts)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested from user {}, remember me={}'.format(form.username.data, \
        form.remember_me.data))
        return redirect(url_for('index'))
    else:
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


