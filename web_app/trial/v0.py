#test version 

from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

#App config
DEBUG = True
app = Flask(__name__)


app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    name = TextField('name:', validators=[validators.required()])

    @app.route("/", methods=['GET', 'POST'])
    def hello():
        #calling the class inside the class
        form = ReusableForm(request.form)
        
        print(form.errors)
        if request.method == "POST":
            name = request.form['name']
            print name
        
        if form.validate():
            #what is flash
            flash("Hello" + name)
        else:
            flash('All the form fields are required')
    return render_template('hello.html', form=form)

if __name__ == "__main__":
    app.run()