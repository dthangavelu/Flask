from flask import Flask, request, redirect, render_template, session, flash

from mysqlconnection import MySQLConnector
import re

app = Flask(__name__)
mysql = MySQLConnector(app,'email_db')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def isValidEmail(email):
	if len(email) > 6:	
		if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email) != None:
			return True
		return False
	return False

@app.route('/')
def index():    
    return render_template('index.html')
	
@app.route('/emails', methods=['post'])
def show_all():  	
	user_email = request.form['email'].lower()
	if len(user_email) == 0:
		flash("The email address can't be blank")
		return redirect("/")
	if isValidEmail(user_email):
		data = {'useremail': user_email}
		email_in_db = mysql.query_db("SELECT * FROM emails where email = :useremail LIMIT 1", data)
		
		if not email_in_db:
			query = 'INSERT INTO emails (email, created_at, updated_at) VALUES(:email, NOW(), NOW())'
			data = {
				'email': user_email,
			}
			mysql.query_db(query, data)
		emails = mysql.query_db("SELECT * FROM emails")
		#if email_in_db:			
		#	email_in_db = email_in_db[0]['email'].lower()
			
		#if user_email == email_in_db:
		#	emails = mysql.query_db("SELECT * FROM emails")    		
		#	return render_template('success.html', all_emails=emails, entered_email = user_email)
		#flash("The email address \"{}\" does not match the one in database. Try again".format(user_email))
		#return redirect("/")
		return render_template('success.html', all_emails=emails, entered_email = user_email)
	flash("The email address \"{}\" is invalid. Format: example@example.xxx".format(user_email))
	return redirect("/")
	
@app.route('/add_email', methods=['GET', 'POST'])
def create():			
	query = "INSERT INTO friends (first_name, last_name, occupation, created_at, updated_at) VALUES (:first_name, :last_name, :occupation, NOW(), NOW())"    
	data = 	{
				'first_name': request.form['first_name'],
				'last_name':  request.form['last_name'],
				'occupation': request.form['occupation'],
			}
	
	mysql.query_db(query, data)
	return redirect('/')
	
app.run(debug=True)

