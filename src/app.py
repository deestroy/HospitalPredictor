import os
import time
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, redirect, url_for

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from models import Hospital


# load environment variables
dotenv_path = '.env'
load_dotenv(dotenv_path)

# initialize flask application
app = Flask(__name__)

# firebase setup
cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)
db = firestore.client()

def format_server_time():
  server_time = time.localtime()
  return time.strftime("%I:%M:%S %p", server_time)

# main page
@app.route('/')
def index():
    context = { 'server_time': format_server_time() }
    return render_template('index.html', context=context)


# 404 page
@app.route('/404')  
def error_page():
    return render_template('404.html')


# data form page
@app.route('/data-form')
def data_form():
    return render_template('data_form.html')


# heat map page
@app.route('/map')
def map():
    hospitals = db.collection('hospitals').stream()    
    data = []
    for hospital in hospitals:
        data.append(hospital.to_dict())
    
    return render_template('map.html', data=data)


# add new hospital data (all fields)
@app.route('/add-hospital-data', methods = ['POST'])
def add_hospital_data():

    if request.method == 'POST':
        req_data = request.get_json()
        hospital = Hospital(req_data['name'], req_data['address'], req_data['city'], req_data['num_beds'], req_data['occupancy'])
        db.collection(u'hospitals').document(req_data['name']).set(hospital.to_dict())
        return redirect(url_for('index'))
    
    return redirect(url_for('error_page'))


# returns data for specified hospital
@app.route('/get-hospital-data', methods = ['POST'])
def get_hospital_data():

    if request.method == 'POST':
        name = request.form['name']

        hospitals = db.collection(u'hospitals').where(u'name', u'==', name).stream()
        
        if len(hospitals) > 0:        
            hospital_data = hospitals[0].to_dict()
            return jsonify(hospital_data)
    
    return redirect(url_for('error_page'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))