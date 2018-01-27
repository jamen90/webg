from flask import Flask,session,render_template,request,redirect,abort,flash,url_for  
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime
import db



app = Flask(__name__)
client = MongoClient('localhost', port=27017)
dbase = client.webg9000


@app.route('/')
def re():
	error=None
	if 'username' in session:
		return redirect(url_for("show_all"))
	return render_template('hello.html', error=error)
	


@app.route('/new_acc', methods=['GET','POST'])
def sign_up():
	error=None
	name = request.form['username']
	password = request.form['password']
	fullname = request.form['fname']
	what = request.form['what']
	where = request.form['where']
	dob = request.form['dob']
	about = request.form['about']
	if request.method == 'POST':
		if name=="" or password=="":
			error="The fields with * are required."
		elif dbase.user.find({"name":name}).count() > 0:
			error="Sorry this name is already existed."
		else:	
			db.User(name).new_acc(password,fullname,what,where,dob,about)
			flash("Welcome {}, You have signed up with us!".format(name))
			session["username"]= name
			return redirect(url_for('show_all', name=name))
	return render_template('hello.html' , error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error=None
	name = str(request.form['uname'])
	pword = str(request.form['pword'])
	if name=="" or pword=="":
		error="fill the both fields"
	else:
		db.User(name).log_in(pword)
		if 'username' in session:
			flash("Welcome back {}".format(name))
			return redirect(url_for('show_all'))
		else:
			error="wrong info.try to log in again"
						
	return render_template('hello.html', error=error)

@app.route('/logout')
def logout():
	uname = session['username']
	db.User(uname).log_out()
	session.pop('username', None)
	return redirect(url_for('re'))



@app.route('/home')
def show_all():
	error=None
	if not session['username']:
		abort(401)
		flash('login or sign-up first')
	else:
		urname = session['username']
		users = dbase.user.find({"name":{"$ne":urname}},{"name":1,"_id":0}).distinct('name')
		title = db.Post.display_all_post()
		return render_template("home.html", users=users, title=title, error=error)

@app.route('/post')
def post_sh():
	error=None
	pid = request.args.get('postid')
	postid = ObjectId(pid)
	#thepost= dbase.post.find({"_id":ObjectId(postid)},{"content":1,"title":1})
	#comments = dbase.post.find({"_id":ObjectId(postid)},{"comment.content":1,"comment.by":1,"_id":0})
	thepost = db.Post.display_post(postid)
	c = db.Post.display_comment(postid)
	if c is not None:
		comments = c.get('comment')
			
	return render_template("post.html", error=error, thepost=thepost, comments=comments, postid=postid)

@app.route('/new_comment', methods=['GET', 'POST'])
def add_comment():
	error=None
	pid = request.args.get('postid')
	postid = ObjectId(pid)
	urname = session['username']
	new_comment = request.form['comment']
	if request.method=='POST':
		if new_comment=="":
			error="write a comment first"
			thepost = db.Post.display_post(postid)
			c = db.Post.display_comment(postid)
			comments = c.get('comment')
			return render_template("post.html", error=error, thepost=thepost, comments=comments, postid=postid)

		else:
			comm = db.Post(new_comment,urname).comment(postid)
			flash("thanks for leaving a comment {}".format(urname))
			thepost = db.Post.display_post(postid)
			c = db.Post.display_comment(postid)
			comments = c.get('comment')

	return render_template("post.html", error=error, thepost=thepost, comments=comments, postid=postid)

def session_chk():
	intime = dbase.user.find({"name":session['username']}).distinct('in-time')
	outtime = dbase.user.find({"name":session['username']}).distinct('out-time')
	if intime > outtime:
		session['username'] = name
		return session['username']
	else:
		session.pop('username', None)
		return None

@app.route('/<profile>')
def ppage(profile):
	error=None
	if 'username' in session:
		if dbase.user.find({"name":profile}).count() > 0:
			if profile == session['username']:
				edit = "Edit"
				other = db.User(profile).display_profile()
				info = strword(other)
				if info[0]=="XPROFILEX":
					info[0]=profile
				#the info have been shown
				ppost = db.User(profile).display_ppost()
				posts = list(ppost)
				comments_num = {}
				for p in posts:
					if p.get('comment'):
						comments_num[p.get('_id')] = len(p.get('comment'))

				return render_template("profile.html", info=info, edit=edit, posts=posts, comments_num=comments_num)				
			else:
				other = db.User(profile).display_profile()
				info = strword(other)
				if info[0]=="XPROFILEX":
					info[0]=profile
				#the info have been shown
				ppost = db.User(profile).display_ppost()
				posts = list(ppost)
				comments_num = {}
				for p in posts:
					if p.get('comment'):

						comments_num[p.get('_id')] = len(p.get('comment'))				
				return render_template("profile.html", info=info, posts=posts, comments_num=comments_num)			
		else:
			error="There's No such a User!"
			return render_template("404.html")
	else:
		abort(401)

@app.route('/add', methods=['POST','GET'])
def add_post():
	error=None
	title = request.form['title']
	text = request.form['text']
	urname = session['username']
	users = dbase.user.find({"name":{"$ne":urname}},{"name":1,"_id":0}).distinct('name')
	title = db.Post.display_all_post()
	if title =="" or text =="":
		error="please fill the both fields."

	else:
		db.Post(text,urname).new_post(title)
		flash("Your Post is on board!")
		return redirect(url_for("show_all"))
	return render_template("home.html", error=error, users=users, title=title)	

@app.route('/edit_info', methods=['GET','POST'])
def edit_info():
	error=None
	urname = session['username']
	other = db.User(urname).display_profile()
	info = strword(other)
	if request.method=='POST':
		db.User(urname).edit_profile(request.form['fname'],request.form['what'],request.form['where'],request.form['dob'],request.form['about'])
		flash("Your info. have been updated")
		return redirect(url_for("show_all"))		

	return render_template("edit_info.html", info=info, error=error)	


def strword(old):
	new = []
	for i in old:
		s1 = i.strip("[")
		s2 = s1.strip("]")
		s3 = s2.strip("'")
		new.append(s3)
	if new[0]=="":
		new[0]="XPROFILEX"
	for f in new:
		if f =="":
			n=new.index(f)
			new[n]="(unknown)"
	return new


if __name__ == "__main__":
	app.secret_key = 'super secret key'
	host = os.environ.get('IP', '0.0.0.0')
	port = int(os.environ.get('PORT', 5000))
	app.run(host=host, port=port) #debug=True)
