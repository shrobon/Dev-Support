import os
from flask import Flask, render_template, request
from werkzeug import secure_filename
import stripe
import re
import markdown
import io
#######################################
#### Imports Necessary for GITHUB LOGIN
#######################################
from flask.ext.github import GitHub
# Set these values
GITHUB_CLIENT_ID = 'a8c6f8e2828251d35ef2'
GITHUB_CLIENT_SECRET = '4546c8ad9a318648c9b7feaf19dc7ddabf5736ae'


app = Flask(__name__)


############################################
## Part of the Stripe Payment Processing ###
############################################

stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

'''
This is needed for the stripe payment 


@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])
'''



@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 500

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

    return render_template('charge.html', amount=amount)


########################################################
### Testing the youtube embed part using RE and embed ##
########################################################

@app.route('/youtube', methods=["GET","POST"])
def youtube():
	return render_template('youtube.html')

@app.route('/video',methods = ["GET","POST"])
def video():
	#I need the author name and the video URL 
	if request.method == "POST":
		url = str(request.form['URL'])
		search = re.match(r'(.*)v=(.*)',url)
		embed_code = search.group(2)
		return render_template('youtube.html',data = embed_code)

	return render_template('link.html')



########################################################
#### File Upload and to Markdown Conversion  ###########
########################################################

@app.route('/upload', methods = ["GET", "POST"])
def markdown_upload():
	if request.method == "GET":
		return render_template('markdownuploader.html')

	if request.method == "POST":
		#grab the contents of the file here 
		f = request.files['markdown']
		f.save(secure_filename(f.filename))

		
		#This is the readme file
		filename = secure_filename(f.filename)

		#Opening the file to read all its contents 
		with open(str("./"+filename),'r') as markdownFile:
			fileContents = markdownFile.read() 


		return render_template('smkdn.html',markdownData = fileContents)
	


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



		return render_template('showgig.html',data = embed_code,markdownData=fileContents,projectname=projectname)

	return render_template('gigform.html')


@app.route('/')
def index():
    return render_template('index.html')


########################################################
#### Github API PART   #################################
########################################################





if __name__ == '__main__':
	app.run(debug= True)




