from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import twitter, jsonpickle
import json
import subprocess
import os, errno
import pymysql as mdb
# import string

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# set database connection 
con = mdb.connect(host = 'localhost', user = 'root', passwd = '@reza27#', db = 'dataset')

@app.route('/', methods=['GET'])
def root():
	# validchars = string.ascii_letters + string.digits + ' '
	passing_data = []
	with con:
		cur = con.cursor()
		cur.execute("SELECT * FROM pariwisata")
		row = cur.fetchall()
		for x in row:
			# s = ''.join(c for c in x[1] if c in validchars)
			passing_data.append([x[2],x[4]])

	return render_template('index.html', data=passing_data)

if __name__ == "__main__":
	app.run()