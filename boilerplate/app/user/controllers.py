from flask import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from app import db
from .models import regUser
from .models import verUser
from app.report.models import Report
from .models import Rating
from werkzeug.security import generate_password_hash, check_password_hash

from flask_cors import CORS

mod_user = Blueprint('user', __name__)
CORS(mod_user)


global a
a=''

@mod_user.route('/',methods=['GET'])
def func():
	if 'roll' not in session and 'email' not in session:
		return redirect('/login')		
	return render_template('index.html')

@mod_user.route('/logout', methods=['GET'])
def logout():
	if 'roll' in session:
		session.pop('roll')
	elif 'email' in session:
		session.pop('email')
	return redirect('/login')
	#return jsonify(success=True, message="Logout Successful")

@mod_user.route('/registerUser', methods=['POST' ,'GET'])
def create_User():
	if 'email' in session:
		session.pop('email')
	if 'roll' in session:
		session.pop('roll')
	if request.method == 'GET':
	
		return render_template('adduser.html')
	else:
		try:
			name = (request.form['name']).lower()
			email = request.form['email']
			password = request.form['password']		
			roll = request.form['roll']
			hostel = request.form['hostel']
			room = request.form['room']
			contact = request.form['contact']
			guardianAdd = request.form['guardianAdd']
			guardianCon = request.form['guardianCon']
		except KeyError as e:
			flash('Please Check your Details')
			return redirect('/registerUser')
				#return jsonify(success=False, message="%s not sent in the request" % e.args), 400
		
		if name=='' or email=='' or password=='' or roll=='' or hostel=='' or room=='' or contact=='' or guardianCon=='' or guardianAdd=='': 
			flash('Please Fill all details')	
			return redirect('/registerUser')
				#return jsonify(success=False, message="Invalid Credentials"), 400

		if '@' not in email:
			flash('Please enter a valid email')
			return redirect('/registerUser')
				#return jsonify(success=False, message="Please enter a valid email"), 400
	
		for i in verUser.query.all():
			if i.email == email:
				flash('This email is in use. Please register with another')
				return redirect('/registerUser')
					#return jsonify(success=False,message="already verified")
	
		user = regUser(name,roll,email,password,hostel,room,contact,guardianCon,guardianAdd,1)
#		user.status = 1
	#	print(user)
		db.session.add(user)

		try:
			db.session.commit()
		except IntegrityError as e:
		#	db.session.rollback()
			flash('This email is in use. Please register with another')
			return redirect('/registerUser')
				#return jsonify(success=False, message="This email already exists"), 400

		flash('You have successfully registered')
		return redirect('/login')
		#return jsonify(success=True)

@mod_user.route('/getAllRegUser', methods=['GET'])
def get_all_reg():
		global a
		a=request.url
		if 'email' not in session:
			 return redirect('/login')
	
		opject = {'users' : []}
		user = regUser.query.all()
		for var in user:
			opject['users'].append(var.serialize())
		return jsonify(opject)

@mod_user.route('/login', methods=['POST' ,'GET'])
def login():
	#a=request.url
		
	global a	
	if request.method == 'GET':
		if 'roll' in session:
			#return session['roll']
			session.pop('roll')
		if 'email' in session:
			session.pop('email')
		#return  a
		return render_template('login1.html')
	else:
		try:
			roll = request.form['roll']
			password = request.form['password']
		except KeyError as e:
			flash('Please Check Your Credentials')
			return redirect('/login')
				#return jsonify(success=False, message="%s not sent in the request" % e.args), 400

		
		user = verUser.query.filter(verUser.roll == request.form['roll']).first()
		#return jsonify(user.ver_check_password('k'))
		if user is None or not user.check_password(password):
			flash('Please Check Your Password')
			return redirect('/login')
				#return jsonify(success=False, message="Invalid Credentials"), 400
		user.authenticated = True

		session['roll'] = roll
		if not a:
			return redirect("/usersearch")
		return redirect(a)
		#return redirect('/usersearch')
		#return jsonify(success=True, message="Login Successfully",user = user.serialize())

@mod_user.route('/usersearch', methods=['GET','POST'])
#@requires_auth_user
def search():
	global a
	a=request.url
	if 'roll' not in session:
		return redirect('/login')
	#print(session['roll'])
	if request.method == 'GET':
		return render_template('usersearch.html')
	else:
		try:
			init = (request.form['enter']).lower()
		except KeyError as e:
			flash('Please check your search query')
			return redirect('/usersearch')
				#return jsonify(success=False, message="%s not sent in the request" % e.args), 400

		users = verUser.query.all()
#		opject = {'results' : []}
		s=[]
		for i in users:
			str1 = i.name
			if(str1.find(init)!=-1):
				s.append(i.serialize2())
		return render_template('user_results.html' , users = s)	

@mod_user.route("/<roll>", methods=['GET'])
#>>>>>>> 983c210d0ea783465b655b31f4c61c6027b9a9c2
def search_roll(roll):
	global a
	a=request.url
	#roll = request.args.get('roll')

	if 'roll' not in session and 'email' not in session:
		return redirect('/login')
	
	user = verUser.query.filter(verUser.roll == roll).first()
	if 'email' in session or session['roll']==roll:
		return render_template('roll-res-private.html' ,user = user.serialize())
	else:
		return render_template('roll-res.html' ,user = user.serialize2())


@mod_user.route("/rate", methods=['GET', 'POST'])
def rate():
	global a
	a = request.url
	if 'roll' not in session:
		return redirect("/login")
	
	users = verUser.query.all()

	if request.method == 'GET':
		return render_template("rateUser.html", users=users)
	else:
		try:
			userRoll = request.form['roll']
		except:
			flash('Please review your response')
			return redirect('/rate')
				#return jsonify(success=False, message="rating not sent in the request"), 400
		
		user = verUser.query.filter(verUser.roll == userRoll).first()
		raterRoll = session['roll']
		response = request.form['option']
		prev = user.rating
		#key = 100000000 * userRoll + raterRoll
		rating = Rating(userRoll,raterRoll,response)
		db.session.add(rating)

		try:
			db.session.commit()
		except IntegrityError as e:
			flash('You have already rated this user')
			return redirect('/rate')	
				#return jsonify(success=False, message="You have already rated this user"), 400
		userRatings = Rating.query.filter(Rating.userRoll == userRoll)
		total = 0
		length=0
		for i in userRatings:
				total = total + i.rating
				length = length + 1
		user.rating = total/length
		try:
			db.session.commit()
		except IntegrityError as e:
			flash('Rating couldnt be submitted')
			return redirect('/rate')
				#return jsonify(success=False, message="rating update error")
		flash('Rating submitted successfully')
		return redirect('/rate')
			#return jsonify(success=True, message="rating submitted")
