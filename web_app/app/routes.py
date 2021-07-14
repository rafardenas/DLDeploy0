import os 
import sys
#sys.path.append(os.getcwd())

from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_migrate import Config, current 
from web_app.app import app, db
from web_app.app.forms import *
from src import config
import torch
import transformers
from src.model import BERTBaseUncased
from flask_login import current_user, login_user, logout_user, login_required
from web_app.app.models import User, Post
from datetime import datetime
from web_app.config2 import Config
from web_app.app.email_mod import *

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


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, user=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Listing is posted now!")
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, Config.POSTS_PER_PAGE, False)   
    #calling a'all' in the last query triggers the execution, we call 'pagination' here instead
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Home Page', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


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
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page) 
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
    return render_template('register.html', title = "Signup", form=form)



@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, Config.POSTS_PER_PAGE, False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()    
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form) 

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)



@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('Now you are following {}'.format(username))
        return redirect (url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You do not follow {} anymore'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))



@app.route('/explore')  #is the default method post?
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, Config.POSTS_PER_PAGE, False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)



@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        flash(user.username)
        if user:
            send_password_reset_email(user)
            flash('Check your email for instructions to reset your password')
            return redirect(url_for('login'))
        else:
            flash('No account with that email, try again')
    return render_template('reset_password_request.html', title='Reset Password', form=form)



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been successfully reset')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


        

