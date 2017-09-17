from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import os, binascii, md5, re

app = Flask(__name__)
mysql = MySQLConnector(app,'users_db')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def isValidEmail(email):
	if len(email) < 7 or re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email) == None:
		return "Email should be of valid format. Format example@example.xxx."
	return True	

def isValidName(name):
	if len(name) < 2:
		return "must be 2 or more characters long"
	if re.match('^[a-zA-Z]+$', name) == None:
		return "only alphabets allowed"
	return True
	
def isValidPwdLen(pwd):
	if len(pwd) < 8:
		return "Password must be of minimum 8 characters long"
	return True

def isPwdMatchesConfirmPwd(pwd, cPwd):
	if pwd != cPwd:
		return "Passwords do not match"
	return True
	
	
@app.route('/')
def index():
	session['user_id'] = 0
	return render_template('index.html')
		
@app.route("/login", methods=['POST','GET'])
def login():
	print "session userid", session['user_id']
	if 'user_id' not in session:
		print "user id not in session*****************"
		return redirect("/")
	
	if session['user_id'] != 0:
		query = "SELECT * FROM users WHERE id = :id LIMIT 1"
		data = {
			'id': session['user_id'],
		}
		current_user = mysql.query_db(query, data)
		#print "current user******************", current_user		
		return render_template("success.html", logged_in_user = (current_user[0]['first_name'] + " " + current_user[0]['last_name']))
		
		
	err_msg = ""
	form_email = request.form['email']
	form_pwd = request.form['password']
	
	if isValidEmail(form_email) != True:
		err_msg += isValidEmail(form_email) + " And it cannot be blank.\n\n"
	if isValidPwdLen(form_pwd) != True:
		err_msg += "Enter valid password. Also password cannot be blank.\n\n"
		
	if len(err_msg) > 0:
		flash("{}".format(err_msg))
		return redirect("/")
	
	query = "SELECT * FROM users where email = :email LIMIT 1"
	data = {
		'email': form_email,
	}
	user = mysql.query_db(query, data)
	if not user:
		flash("Your email is not in system. Please register.")
		return redirect("/")
	
	db_password = user[0]['password']
	salt = user[0]['salt']
	hashed_pw = md5.new(form_pwd + salt).hexdigest()
	if db_password != hashed_pw:
		flash("Please enter correct password.")
		return redirect("/")
	session['user_id'] = user[0]['id']
	return render_template("success.html", logged_in_user = (user[0]['first_name'] + " " + user[0]['last_name']))	

	
@app.route('/register', methods=['GET', 'POST'])
def register():	
	if 'user_id' not in session:
		return redirect("/")
		
	if session['user_id'] != 0:
		query = "SELECT * FROM users WHERE id = :id LIMIT 1"
		data = {
			'id': session['user_id'],
		}
		current_user = mysql.query_db(query, data)
		#print "current user******************", current_user		
		return render_template("success.html", logged_in_user = (current_user[0]['first_name'] + " " + current_user[0]['last_name']))
			
	form_fn = request.form['first_name']
	form_ln = request.form['last_name']
	form_email = request.form['email']
	form_pwd = request.form['password']
	form_confirm_pwd = request.form['confirm_password']
	err_msg = ""
	
	if isValidName(form_fn) != True:
		err_msg += "First Name " + isValidName(form_fn) + "\n\n"
	if isValidName(form_ln) != True:
		err_msg += "Last Name " + isValidName(form_ln) + "\n\n"
	if isValidEmail(form_email) != True:
		err_msg += isValidEmail(form_email) + "\n\n"
	if isValidPwdLen(form_pwd) != True:
		err_msg += isValidPwdLen(form_pwd) + "\n\n"
	if isPwdMatchesConfirmPwd(form_pwd, form_confirm_pwd) != True:
		err_msg += isPwdMatchesConfirmPwd(form_pwd, form_confirm_pwd)
		
	if len(err_msg) > 0:
		flash("{}".format(err_msg))
		return redirect("/")
		
	salt = binascii.b2a_hex(os.urandom(15))
	hashed_pw = md5.new(form_pwd + salt).hexdigest()
	
	query = "INSERT INTO users (first_name, last_name, password, salt, email, created_at, updated_at) VALUES (:first_name, :last_name, :password, :salt, :email, NOW(), NOW())"    
	data = 	{
				'first_name': form_fn,
				'last_name':  form_ln,
				'password': hashed_pw,
				'salt': salt,
				'email': form_email,
			}
	
	user_id = mysql.query_db(query, data)
	
	session['user_id'] = user_id
	#if 'user_id' in session:
	return render_template("success.html", logged_in_user = (form_fn + " " + form_ln))

@app.route("/logout")
def logout():
	session.clear()	
	return redirect("/")
	
app.run(debug=True)

