from flask import Blueprint, request, render_template, \
				  flash, g, session, redirect, url_for,jsonify,make_response
from app import db
from app.report.models import Report
#from app.report.models import Comments
from app.user.models import verUser
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from .models import Comments

mod_report = Blueprint('report', __name__)
CORS(mod_report)

global a
a = ''

@mod_report.route('/addComplaint', methods=['GET', 'POST'])
def addComplaint():
		global a
		a = request.url
		if 'roll' not in session:
				return redirect('/login')

		if request.method == 'GET':
				return render_template('addComplaint.html')
		else:
				try:
					if 'roll' in session:
							roll = session['roll']
					else:
							roll = session['email']
					title = request.form['About']
					complaint = request.form['comp']
				except KeyError as e:
					flash('Please Fill Correct details')
					return redirect('/addComplaint')
					#return jsonify(success=False, message="%s not sent in request" % e.args), 400

				user = verUser.query.filter(verUser.roll == roll).first()
				print(user)

				if user is None:
					flash('Please Login')
					return redirect('/login')
					#	return jsonify(success=False, message="Invalid Credentials"), 400

				done = Report(roll, title, complaint, )
				print(done)
				db.session.add(done)
				
				try:
					db.session.commit()
				except IntegrityError as e:
					flash('Complaint already exists')
					return redirect('/addComment')
					#return jsonify(success=False, message="Complaint already exists")
				flash('Complaint Recorded')
				return redirect('/addComment')
				#return jsonify(success=True, message="Your complaint has been recorded")

@mod_report.route('/getAllComplaints', methods=['GET'])
def get_all():
		global a
		a = request.url
		if 'email' and 'roll' not in session:
			return redirect('/login')
		opject = {'complaints' : []}
		comp = Report.query.all()
		for var in comp:
			opject['complaints'].append(var.serialize())
		return jsonify(opject)

@mod_report.route('/getAllComments',methods=['GET'])
def get_comm():
		global a
		a = request.url
		if 'email' and 'roll' not in session:
			return redirect('/login')
		opject = {'comments' : []}
		comp = Comments.query.all()
		for var in comp:
			opject['comments'].append(var.serialize())
		return jsonify(opject)

@mod_report.route('/complaint/<title>',methods=['GET'])
def get_complain(title):
	comp = Report.query.filter(Report.title == title).first()
	if comp is None:
		return redirect('/addComplaint')
	else:
		a = Comments.query.filter_by(rid = comp.id).all()
		print (a)
		#arr = []
		#for i in Comments.query.all():
		#	if i.rid == comp.id:
		#		arr.append(i)
		#opject['arr'].append(arr)
		#opject['rep']=comp
		print ([i.serialize() for i in a])
		opject = {'arr': [i.serialize() for i in a],'comp':[comp.serialize()]}
		return render_template('comment-res.html',users=opject)
		#return jsonify(opject)

@mod_report.route('/addComment', methods=['GET', 'POST'])
def comment():
	global a
	a = request.url
	if "roll" not in session:
		return redirect("/login")
	reports = Report.query.all()
	
	if request.method == 'GET':
		return render_template('addComment.html', reports=reports)
	else:
		try:
			if 'roll' in session:
					roll = session['roll']
			# 	else:
			#		roll = session['email']
			title = request.form['title']
		except:
			flash('Error')
			return redirect('/addComment')
			#return jsonify(success=False, message="%s not sent in the request" % e.args), 400
		#print(title)
		#comp = Report.query.filter(Report.title == title).first()
		#rid = comp.id
		#print(comp)

		for i in Report.query.all():
			if(i.title == title):
				comp = i
		rid = comp.id
		text = request.form['comment']

		comm = Comments(roll,text,rid)
		db.session.add(comm)
		db.session.commit()
		flash('Comment Recorded')
		return redirect('/complaint/'+comp.title)
		#return jsonify(success=True, message="Your comment has been recorded")
