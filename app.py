from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from module.icicm import ICICM
import glob, os
import numpy as np

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wisata_madura.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)
icicm = ICICM()

class ReusableForm(Form):
	query = TextField('Text Query:', validators=[validators.required()])

class Pariwisata(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_str = db.Column(db.Text)
	tweet = db.Column(db.Text)
	image_url = db.Column(db.Text)
	image_fname = db.Column(db.Text)

@app.route('/', methods=['GET'])
def root():
	data = Pariwisata.query.all()
	return render_template('index.html', data=data)

@app.route('/<int:id>', methods=['GET'])
def get_similar_images(id):
	row = Pariwisata.query.get(id)
	# print(row.image_fname)
	q_factor = 8
	h_q,s_q,v_q = icicm.rgb_to_hsv('/home/reza/skripsi/tourism_retrieval/static/assets/images/pariwisata/'+row.image_fname)
	icicm_q = icicm.icicm_feature(q_factor, h_q, s_q, v_q)

	path = '/home/reza/skripsi/tourism_retrieval/static/assets/images/pariwisata/*.jpg'
	# print(path.split('/')[6:])
	img_path = sorted([x for x in glob.glob(path)], key=icicm.natural_keys)
	# print(img_path[1][44:])
	sim_mat = []
	for idx, img in enumerate(img_path):
		print('Process image-> ', idx)
		h_d,s_d,v_d = icicm.rgb_to_hsv(img)
		icicm_d = icicm.icicm_feature(q_factor, h_d, s_d, v_d)
		sim_mat.append(icicm.manhattan_distance(icicm_q, icicm_d))

	result = []
	sorted_similarity = np.argsort(np.array(sim_mat))
	for idx in sorted_similarity:
		result.append(img_path[idx][44:])    
	return render_template('get_by_id.html', id=id, data=result)

@app.route('/text', methods=['GET', 'POST'])
def text():
	form = ReusableForm(request.form)
	query = ""
	passing_data = []

	if request.method == 'POST':
		query = request.form['query']

		if form.validate():
			passing_data = Pariwisata.query.filter(Pariwisata.tweet.like('%'+query+'%')).all()
		else:
			flash('All the form fields are required. ')

	return render_template('text.html', data=passing_data, form=form, query=query)

if __name__ == "__main__":
	toolbar.init_app(app)
	app.run()