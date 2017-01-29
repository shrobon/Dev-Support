# -*- coding: utf-8 -*-
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

from flask.ext.pymongo import PyMongo

import os 
import stripe




#I am using this for stripe payments 
stripe_keys = {
  'secret_key': 'sk_test_pBOsfFhf1SPeP7XfFLmlwi8o',
  'publishable_key': 'pk_test_5PT5eNn5SEl8jdnmlxBAGZxB'
}

stripe.api_key = stripe_keys['secret_key']





DATABASE_URI = 'sqlite:///github-flask.db'
SECRET_KEY = 'development key'
DEBUG = True

# Github App Registration
GITHUB_CLIENT_ID = '7be478dde53db06a83bb'
GITHUB_CLIENT_SECRET = '53d420511f625512cad0b483eb99c09d17a8807e'


# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

########### This is for the stripe part #####################
####





###### Setting the cconfigurating for MONGODB #########
app.config['MONGO_DBNAME'] = "connect_to_mongo"
app.config['MONGO_URI'] = "mongodb://shrobon:biswas@ds133279.mlab.com:33279/connect_to_mongo"
mongo = PyMongo(app)
## check in terminal from mongo_connect import mongo

@app.route('/ty', methods=['POST'])
def charge():
    # Amount in cents
    amount = 5000

    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )


    ## Fetching the user and project from the showgig page so that i can 
    ## read the database and see which is the dropbox link for that project 
    user = request.form['user']
    project = request.form['project']


    ## Searching the database for the corresponding project 
    users = mongo.db.user
    results = users.find_one({'name': user})
    index = results['gigs'].index(project)

    return render_template('ty.html', amount=amount, dropbox = results['dropbox'][index])


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




class Info():

    userDict=dict()

    def __init__(self,userDict):
        self.userDict = userDict



########################################################
#### File Upload and to Markdown Conversion  ###########
########################################################
@app.route('/showgig',methods = ["GET","POST"])
def showgig():
    # This view function will only get POST request
    #I need the author name and the video URL 
    if request.method == "POST":
        url = str(request.form['URL'])
        search = re.match(r'(.*)v=(.*)',url)
        embed_code = search.group(2)

        f = request.files['markdown']
        '''
        f.save(secure_filename(f.filename))
        #This is the readme file
        filename = secure_filename(f.filename)
        #Opening the file to read all its contents 
        with io.open(str("./"+filename),'r',encoding='utf8') as markdownFile:
            fileContents = markdownFile.read() 
        '''
        fileContents = f.read(charset='utf-8')
        projectname = str(request.form['projectname']).strip()
        description = str(request.form['description']).strip()
        dropbox = str(request.form['dropbox']).strip()
        dropbox=dropbox.replace("dl=0","dl=1") # I need to add a test case here 


        ## Fetching all user Infor for gig page
        #######################################
        UserDict =  Info.userDict # This returns a dictionary
        avatar = UserDict['avatar_url']
        name = UserDict['name']
        location = UserDict['location']
        email = UserDict['email']
        giturl = UserDict['html_url']

        ## Genrating the dynamic link where i can find the project portfolio 
        link = "https://devsupport.herokuapp.com/explore/"+ giturl.split('https://github.com/')[1]+'/'+projectname




        #######################################################################
        ## Since gig is posted, lets add it to the collection of the users gigs
        #######################################################################
        users = mongo.db.user
        users.update({'email':email},{'$push':{'gigs':projectname,'youtube':embed_code,'MDcontents':fileContents,'dropbox':dropbox,'thumbsup':0}})

        ##########################################################
        ## Also adding the link to the explorelinks mongo document
        ##########################################################
        explore_links = mongo.db.explorelinks
        explore_links.insert({'link':link,'gigs':projectname,'description':description,'embed_code':embed_code,'thumbsup':0})





        return render_template('showgig.html',data = embed_code\
            ,markdownData=fileContents,projectname=projectname\
            ,avatar=avatar,name=name,location=location,email=email,giturl=giturl,key=stripe_keys['publishable_key'])

    if request.method == "GET":
        # GET request is not valid for this URL route 
        # Maybe flash a message if necessary
        return redirect(url_for("index"))


@app.route('/gigform',methods=["GET"])
def gigform():
    # This URL will only get get Requests
    if request.method == "GET" and session.get('user_id', None) is not None:
        # I need to fetch the user details over here 
        # Wish the User a Hello with his picture 
        UserDict =  github.get('user') # This returns a dictionary

        #passing the information to the Info Classs such that it can be accessed by all other routes 
        Info.userDict = UserDict

        avatar = UserDict['avatar_url']
        name = UserDict['name']
        location = UserDict['location']
        email = UserDict['email']
        giturl = UserDict['html_url']

        ###  DATABASE LOGIC #####################################
        ## If the user does not exist in database then add him ##
        #########################################################
        gigs = []
        users = mongo.db.user
        link= ""
        x= users.find_one({'email': email})
        if x is None:
            users.insert({'email':email,'gigs':[],'MDcontents':[],'youtube':[],'avatar':avatar,'location':location,'name':giturl.split('https://github.com/')[1]})

        else:
            #This is an existing user :: check if he has any projects already 
            # if yes , we need to send the data to the created gigs tab 
            info = users.find_one({'email':email})
            gigs= info['gigs']
            link = "https://devsupport.herokuapp.com/explore/"+ giturl.split('https://github.com/')[1]+'/'

        return render_template('gigform1.html',avatar=avatar,name=name\
            ,location=location,email=email,giturl=giturl,gigs=gigs,link=link)

    else:
        return "You are unauthorized to access this page. Consider logging in "







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
    return redirect(url_for('gigform'))






@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize()
    else:
        return 'Already logged in'







@app.route('/logout')
def logout():
    # I need to remove the tokens from the database too 
    # BUT
    # Flask will automatically remove database sessions 
    # at the end of the request or when the application shuts down
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



#############################################
#### Explore Page 
#### Need to dynamically generate the cards
#############################################
@app.route('/explore/<string:user>/<string:gig>',methods=["POST","GET"])
def dynamic_page(user,gig):
    if request.method == "GET":
        #check if the user exists and the gig exists 
        # if so then link is valid.
            # then get all the user details and populate the page of showgig
        #return user+' '+gig
        
        users = mongo.db.user
        data= users.find_one({'name': user})
        gigs= data['gigs']


        if gig !="" and user != "":
            if gig in gigs:
                #This means that the gig exists
                index = gigs.index(gig)
                embed_code= data['youtube'][index]
                fileContents = data['MDcontents'][index]
                avatar = data['avatar']
                location = data['location']
                email = data['email']
                projectname = gig


                explorelinks = mongo.db.explorelinks
                ## query the explore links database 
                data1 = explorelinks.find_one({'gigs':gig})
                likes = data1['thumbsup']


                return render_template('showgig.html',data = embed_code\
                    ,markdownData=fileContents,projectname=projectname\
                    ,avatar=avatar,location=location,email=email,user=user,key=stripe_keys['publishable_key'],likes=likes)

            else:
                #This is not a valid project
                return render_template('notfound.html', pic='/static/404.png'), 404




    if request.method == "POST":
        # This has been done to increase the like counter for the project
        users = mongo.db.user
        data= users.find_one({'name': user})
        gigs= data['gigs']
        if gig !="" and user != "":
            if gig in gigs:
                #This means that the gig exists
                index = gigs.index(gig)
                embed_code= data['youtube'][index]
                fileContents = data['MDcontents'][index]
                avatar = data['avatar']
                location = data['location']
                projectname = gig

                explorelinks = mongo.db.explorelinks
                ## query the explore links database 
                data1 = explorelinks.find_one({'gigs':gig})
## changes made here 
                likes = data1['thumbsup']
                #incrementing the like counter 
                likes = int(likes) + 1
                #updating the like counter in mongodb
                explorelinks.update({'gigs':gig},{'$set':{'thumbsup':likes}})

                return render_template('showgig.html',data = embed_code\
                    ,markdownData=fileContents,projectname=projectname\
                    ,avatar=avatar,location=location,user=user,key=stripe_keys['publishable_key'],likes=likes)

            else:
                #This is not a valid project
                return render_template('notfound.html', pic='/static/404.png'), 404


        



@app.route('/explore',methods=["GET"])
def explore():

    #this is another collection that contains the the links of projects to explore
    explore_links = mongo.db.explorelinks.find().limit(12)
    description = []
    gigs = []
    links = []
    embed_code= []
    # we need to iterate mongodb cursors in this particular way only 
    for record in explore_links:
        #desc = record['description']
        description.append(record['description'])
        gigs.append(record['gigs'])
        links.append(record['link'])
        embed_code.append(record['embed_code'])


    return render_template('explore.html',video=embed_code,title = gigs, description=description,link=links,length=len(links))




#############################################
## To tackle bad content requests
#############################################
@app.errorhandler(404)
def not_found_error(error):
    return render_template('notfound.html', pic='/static/404.png'), 404




if __name__ == '__main__':
    init_db()
    app.run(debug=True)
