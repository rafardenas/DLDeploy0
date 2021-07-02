from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

#encapsulate each of the forms in one class

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])    #validators argument is to check that field is not empty
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class pred_form(FlaskForm):
    sentence = StringField('Sentence', validators=[DataRequired()])
    submit = SubmitField("I'm feeling lucky")