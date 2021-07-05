#don't forget to set the 'FLASK_APP' env variable

import os 
import sys
#sys.path.append("..") #this was the key for everything
#sys.path.append(".") #this was the key for everything
sys.path.append(os.getcwd())
print(os.environ.get('FLASK_APP'))
print(sys.path)

from web_app.app import app, db
from web_app.app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db' : db, 'User' : User, 'Post': Post}


if __name__ == "__main__":
    app.run()

