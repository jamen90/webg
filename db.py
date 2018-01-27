from pymongo import MongoClient
import os
import datetime
from flask import abort, flash, session,redirect,url_for
from bson.objectid import ObjectId


client = MongoClient('localhost', port=27017)
dbase = client.webg9000

class User:


	def __init__(self,name):
		#to insert a new user
		self.name = name
		

	def new_acc(self,password,fullname,what,where,dob,about):
		self.password = password
		self.fullname = fullname
		self.what = what
		self.where = where
		self.dob = dob
		self.about = about	
		new_acc = {	"name":self.name,
					"password":self.password,
					"in-time":datetime.datetime.utcnow(),
					"out-time":datetime.datetime.utcnow(),
					"other":{
							"fullname":self.fullname,
							"what":self.what,
							"where":self.where,
							"dob":self.dob,
							"about":self.about
							}
					}
		insert = dbase.user.insert_one(new_acc)


	def log_in(self,password):
		#to log-in
		self.password = password
		if dbase.user.find({"name":self.name , "password":self.password}).count() > 0:
			new_log = dbase.user.update({"name":self.name, "password":self.password},{"$set": {"in-time":datetime.datetime.utcnow()}})			
			session['username'] = self.name
			return session['username']
		else:
			return None


	def log_out(self):
		outt = dbase.user.update({"name":self.name},{"$set": {"out-time":datetime.datetime.utcnow()}})
		return None

	def display_profile(self):
		fullname = str(dbase.user.find({"name":self.name},{"other.fullname":1, "_id":0}).distinct('other.fullname'))
		what = str(dbase.user.find({"name":self.name},{"other.what":1, "_id":0}).distinct('other.what'))
		where = str(dbase.user.find({"name":self.name},{"other.where":1, "_id":0}).distinct('other.where'))
		dob = str(dbase.user.find({"name":self.name},{"other.dob":1, "_id":0}).distinct('other.dob'))
		about = str(dbase.user.find({"name":self.name},{"other.about":1,"_id":0}).distinct('other.about'))
		other = (fullname,what,where,dob,about)
		return other

	def edit_profile(self,nfull,nwhat,nwhere,ndob,nabout):
		self.nfull = nfull
		self.nwhat = nwhat
		self.nwhere = nwhere
		self.ndob = ndob
		self.nabout = nabout
		updated = dbase.user.update({"name":self.name},{"$set": {"other.fullname":self.nfull,"other.what":self.nwhat,"other.where":self.nwhere,"other.dob":self.ndob,"other.about":self.nabout}})
		return None

	def display_ppost(self):
		upost1 = dbase.user.find_one({"name":self.name},{"posts":1, "_id":0})
		upost2 = upost1.get('posts')
		posts = []
		if upost2 is not None:
			for q in upost2:
				for e in q:
					posts.append(e)

		post = dbase.post.find({"_id":{"$in":posts}})
		return post


class Post:


	def __init__(self,content,by):

		self.content=content
		self.by = by


	def new_post(self,title):
		self.title=title
		post = {"title":self.title,
				"content":self.content,
				"by":self.by,
				"date":datetime.datetime.utcnow()
			}
		new = dbase.post.insert_one(post)
		postid = dbase.post.find({"title":self.title, "content":self.content, "by":self.by}).distinct('_id')
		userref = dbase.user.update({"name":self.by},{"$push": {"posts": postid  }})

		return None

	def display_all_post():
		t = dbase.post.find({},{"title":1,"by":1,"_id":1}).sort("date",-1)
		return t

	def display_post(pid):
		
		post = dbase.post.find({"_id":ObjectId(pid)},{"title":1,"content":1,"by":1,"_id":1})
		return post

	def comment(self,pid):
		self.pid = pid
		new = dbase.post.update({"_id":ObjectId(self.pid)},{"$push":{'comment': {'content':self.content, 'by':self.by, 'date':datetime.datetime.utcnow()}}})
		return 

	def display_comment(pid):
		comment = dbase.post.find_one({"_id":ObjectId(pid)},{"comment.content":1,"comment.by":1,"_id":0})
		return comment




#class Inbox:


#	def __init__(self,von,inhalt):
#		self.von. = von
#		self.inhalt = inhalt

#	def send(self,to):
#		self.to = to
#		new_message = {"from":self.von,
#					   "inhalt":self.inhalt,
#					   "to":self.to,
#					   "date":datetime.datetime.utcnow()
#				}

#		dbase.inbox.insert_one(new_message)

#	def mybox(self,mich):
#		self.mich = mich
#		dbase.inbox.find({"to":self.mich})
