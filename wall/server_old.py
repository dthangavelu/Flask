from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import os, binascii, md5, re

app = Flask(__name__)
mysql = MySQLConnector(app,'wall_db')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def isValidEmail(email):
	if len(email) < 7 or re.match('[^@]+@[^@]+\.[^@]+', email) == None:
		return "Email should be of valid format. Format example@example.xx[xx]."
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
		
@app.route("/wall", methods=['POST','GET'])
def login():
	print "session userid", session['user_id']
	if 'user_id' not in session:
		print "user id not in session*****************"
		return redirect("/")
	
	msg_count_in_db = mysql.query_db("SELECT count(*) as msgCount FROM messages")
	msg_count_in_db = msg_count_in_db[0]['msgCount']
	
	query = "SELECT users.id as msg_owner_id, CONCAT(first_name, ' ', last_name) as msg_owner, messages.id as msg_id, messages.message, date_format(messages.updated_at, '%b %d %Y, %l:%i %p') as updated_at FROM users JOIN messages ON users.id = messages.user_id ORDER BY updated_at DESC"
	all_msgs_in_db = mysql.query_db(query)
	
	query = "SELECT comment, date_format(comments.created_at, '%b %d %Y, %l:%i %p') as created_at, date_format(comments.updated_at, '%b %d %Y, %l:%i %p') as updated_at, comments.message_id, comments.user_id, concat(users.first_name, ' ', users.last_name) as comment_user FROM comments JOIN users ON users.id = comments.user_id;"	
	all_cmts_for_a_msg = mysql.query_db(query)
	
	if session['user_id'] != 0:
		query = "SELECT * FROM users WHERE id = :id LIMIT 1"
		data = {
			'id': session['user_id'],
		}
		current_user = mysql.query_db(query, data)	
		return render_template("wall.html",  id=session['user_id'], logged_in_user = session['user_name'], msg_count = msg_count_in_db, all_msgs = all_msgs_in_db, all_cmts = all_cmts_for_a_msg)
		
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
	session['user_name'] = (user[0]['first_name'] + " " + user[0]['last_name'])	
	return render_template("wall.html",  id=session['user_id'], logged_in_user = session['user_name'], msg_count = msg_count_in_db, all_msgs = all_msgs_in_db, all_cmts = all_cmts_for_a_msg)
	
@app.route('/register', methods=['GET', 'POST'])
def register():	
	if 'user_id' not in session:
		return redirect("/")
	
	msg_count_in_db = mysql.query_db("SELECT count(*) as msgCount FROM messages")
	msg_count_in_db = msg_count_in_db[0]['msgCount']
	
	query = "SELECT users.id as msg_owner_id, CONCAT(first_name, ' ', last_name) as msg_owner, messages.id as msg_id, messages.message, date_format(messages.updated_at, '%b %d %Y, %l:%i %p') as updated_at FROM users JOIN messages ON users.id = messages.user_id ORDER BY updated_at DESC"
	all_msgs_in_db = mysql.query_db(query)
	
	query = "SELECT comment, date_format(comments.created_at, '%b %d %Y, %l:%i %p') as created_at, date_format(comments.updated_at, '%b %d %Y, %l:%i %p') as updated_at, comments.message_id, comments.user_id, concat(users.first_name, ' ', users.last_name) as comment_user FROM comments JOIN users ON users.id = comments.user_id;"	
	all_cmts_for_a_msg = mysql.query_db(query)
	
	if session['user_id'] != 0:
		query = "SELECT * FROM users WHERE id = :id LIMIT 1"
		data = {
			'id': session['user_id'],
		}
		current_user = mysql.query_db(query, data)
	
		return redirect("/wall")
		
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
	session['user_name'] = (form_fn + " " + form_ln)
	
	return redirect("/wall")

@app.route("/logout")
def logout():
	session.clear()	
	return redirect("/")

@app.route("/post_msg", methods=['GET', 'POST'])
def post_msg():
	form_msg = request.form['msg_txt']
	form_user_id = request.form['msg_user_id']
	msg_count_in_db = mysql.query_db("SELECT count(*) as msgCount FROM messages")
	msg_count_in_db = msg_count_in_db[0]['msgCount']
	
	query = "SELECT users.id as msg_owner_id, CONCAT(first_name, ' ', last_name) as msg_owner, messages.id as msg_id, messages.message, date_format(messages.updated_at, '%b %d %Y, %l:%i %p') as updated_at FROM users JOIN messages ON users.id = messages.user_id ORDER BY updated_at DESC"
	all_msgs_in_db = mysql.query_db(query)
	
	query = "SELECT comment, date_format(comments.created_at, '%b %d %Y, %l:%i %p') as created_at, date_format(comments.updated_at, '%b %d %Y, %l:%i %p') as updated_at, comments.message_id, comments.user_id, concat(users.first_name, ' ', users.last_name) as comment_user FROM comments JOIN users ON users.id = comments.user_id;"	
	all_cmts_for_a_msg = mysql.query_db(query)
	
	if len(form_msg) <= 0:
		flash("Please enter message before posting.")
		return redirect("/wall")
	
	query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES(:message, :user_id, NOW(), NOW())"
	data = {
		'message': form_msg,
		'user_id': form_user_id,
	}
	user_msg_id = mysql.query_db(query, data)
	
	msg_count_in_db = mysql.query_db("SELECT count(*) as msgCount FROM messages")
	msg_count_in_db = msg_count_in_db[0]['msgCount']
	
	query = "SELECT users.id as msg_owner_id, CONCAT(first_name, ' ', last_name) as msg_owner, messages.id as msg_id, messages.message, date_format(messages.updated_at, '%b %d %Y, %l:%i %p') as updated_at FROM users JOIN messages ON users.id = messages.user_id ORDER BY updated_at DESC"

	all_msgs_in_db = mysql.query_db(query)
	
	query = "SELECT comment, date_format(comments.created_at, '%b %d %Y, %l:%i %p') as created_at, date_format(comments.updated_at, '%b %d %Y, %l:%i %p') as updated_at, comments.message_id, comments.user_id, concat(users.first_name, ' ', users.last_name) as comment_user FROM comments JOIN users ON users.id = comments.user_id;"	
	all_cmts_for_a_msg = mysql.query_db(query)
	
	return redirect("/wall")


@app.route("/post_comment", methods=['GET', 'POST'])
def post_comment():			
	comment_txt = request.form['comment_txt']
	comment_user_id = request.form['comment_user_id']
	msg_id = request.form['msg_id']	
	
	msg_count_in_db = mysql.query_db("SELECT count(*) as msgCount FROM messages")
	msg_count_in_db = msg_count_in_db[0]['msgCount']
	query = "SELECT users.id as msg_owner_id, CONCAT(first_name, ' ', last_name) as msg_owner, messages.id as msg_id, messages.message, date_format(messages.updated_at, '%b %d %Y, %l:%i %p') as updated_at FROM users JOIN messages ON users.id = messages.user_id ORDER BY updated_at DESC"
	all_msgs_in_db = mysql.query_db(query)
	
	if len(comment_txt) > 0:		
		query = "INSERT INTO comments (comment, user_id, message_id, created_at, updated_at) VALUES(:comment, :user_id, :message_id, NOW(), NOW())"
		data = {
			'comment': comment_txt,
			'user_id': comment_user_id,
			'message_id': msg_id,
		}
		comment_id = mysql.query_db(query, data)
		
		query = "SELECT comment, date_format(comments.created_at, '%b %d %Y, %l:%i %p') as created_at, date_format(comments.updated_at, '%b %d %Y, %l:%i %p') as updated_at, comments.message_id, comments.user_id, concat(users.first_name, ' ', users.last_name) as comment_user FROM comments JOIN users ON users.id = comments.user_id;"	
		all_cmts_for_a_msg = mysql.query_db(query)		
		
	flash("Please enter comment before posting")
	
	return redirect("/wall")	
	
app.run(debug=True)

