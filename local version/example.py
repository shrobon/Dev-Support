from flask import Flask, request, g, session, redirect, url_for
from flask import render_template_string , render_template
from flask.ext.github import GitHub
from flask import jsonify
#import json

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



from werkzeug import secure_filename
import stripe
import re
import markdown
import io


DATABASE_URI = 'sqlite:////tmp/github-flask.db'
SECRET_KEY = 'development key'
DEBUG = True

# Github App Registration
GITHUB_CLIENT_ID = 'a8c6f8e2828251d35ef2'
GITHUB_CLIENT_SECRET = '4546c8ad9a318648c9b7feaf19dc7ddabf5736ae'


# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# setup github-flask
github = GitHub(app)




# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()







def init_db():
    Base.metadata.create_all(bind=engine)


####################################
### Creating the SQLite3 DB Schema #
####################################
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    github_access_token = Column(String(200))

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token






@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response







@app.route('/')
def index():
    #Checks if the user is logged out or logged in based on the session
    if g.user:
        # Means session exists and the user is logged in 
        state="Logout"
        link =  url_for("logout")
        
    else:
        state = "Github Login"
        link =  url_for("login")

    return render_template('index.html',LoginOrLogout=state,ButtonLink=link)








########################################################
#### File Upload and to Markdown Conversion  ###########
########################################################
@app.route('/showgig',methods = ["GET","POST"])
def showgig():

    #I need the author name and the video URL 
    if request.method == "POST":
        url = str(request.form['URL'])
        search = re.match(r'(.*)v=(.*)',url)
        embed_code = search.group(2)

        f = request.files['markdown']
        f.save(secure_filename(f.filename))
        #This is the readme file
        filename = secure_filename(f.filename)
        #Opening the file to read all its contents 
        with io.open(str("./"+filename),'r',encoding='utf8') as markdownFile:
            fileContents = markdownFile.read() 

        projectname = str(request.form['projectname'])

        ## Fetching all user Infor for gig page
        #######################################
        UserDict =  github.get('user') # This returns a dictionary
        avatar = UserDict['avatar_url']
        name = UserDict['name']
        location = UserDict['location']
        email = UserDict['email']
        giturl = UserDict['html_url']

        return render_template('showgig.html',data = embed_code\
            ,markdownData=fileContents,projectname=projectname\
            ,avatar=avatar,name=name,location=location,email=email,giturl=giturl)




    if request.method == "GET":
        # I need to fetch the user details over here 
        # Wish the User a Hello with his picture 
        UserDict =  github.get('user') # This returns a dictionary
        avatar = UserDict['avatar_url']
        name = UserDict['name']
        location = UserDict['location']
        email = UserDict['email']
        giturl = UserDict['html_url']

        return render_template('gigform1.html',avatar=avatar,name=name\
            ,location=location,email=email,giturl=giturl)








@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token



@app.route('/error')
def unauth():
    return "Unauthorized Access :: Invalid Password"


###############################################
## Callback page after the Auth is successfull
###############################################
@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = url_for('unauth')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    
    if user is None:
        user = User(access_token)
        db_session.add(user)

    user.github_access_token = access_token
    db_session.commit()

    session['user_id'] = user.id
    return redirect(url_for('showgig'))






@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize()
    else:
        return 'Already logged in'


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))



##########################################
#### Fetching the user Json Information ##
#### Note ::-- Use this for the user Profile Info 
##########################################
@app.route('/user')
def user():
    UserDict =  github.get('user') # This returns a dictionary
    # Try seeing it in the browser using jsonify()
    #avatar = UserDict['location']
    return jsonify(UserDict)


    

if __name__ == '__main__':
    init_db()
    app.run(debug=True)