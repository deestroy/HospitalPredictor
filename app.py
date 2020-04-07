import os
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

hospital_data = \
[
    {
        'name': 'The Ottawa Hopsital, General Campus',
        'address': '501 Smyth Road',
        'city': 'Ottawa',
        'num_beds': 1232,
        'occupancy': 0.76
    },
    {
        'name': 'CHEO',
        'address': '401 Smyth Road',
        'city': 'Ottawa',
        'num_beds': 167,
        'occupancy': 0.76
    }
]


# main page
@app.route('/')
def index():
    return render_template('index.html')


# 404 page
@app.route('/404')  
def error_page():
    return render_template('404.html', data=hospital_data)


@app.route('/hospital-data', methods = ['GET'])
def get_all_hospital_data():
    hospitals = db.collection('hospitals').stream()    
    data = []
    for hospital in hospitals:
        data.append(hospital.to_dict())
    
    return render_template('404.html', data=data)


# update existing hospital with new data (all fields)
@app.route('/add-hospital-data', methods = ['GET', 'POST'])
def add_hospital_data():

    # DUMMY DATA FOR TESTING
    if request.method == 'GET':
        for hospital in hospital_data:
            db.collection(u'hospitals').document(hospital['name']).set(hospital)
        return redirect(url_for('index'))

    elif request.method == 'POST':
        req_data = request.get_json()
        hospital = Hospital(req_data['name'], req_data['address'], req_data['city'], req_data['num_beds'], req_data['occupancy'])
        db.collection(u'hospitals').document(req_data['name']).set(hospital.to_dict())
        return redirect(url_for('index'))
    
    return redirect(url_for('error_page'), data=hospital_data)


# returns data for specified hospital
@app.route('/get-hospital-data', methods = ['POST'])
def get_hospital_data():

    if request.method == 'POST':
        name = request.form['name']

        hospitals = db.collection(u'hospitals').where(u'name', u'==', name).stream()
        
        if len(hospitals) > 0:        
            hospital_data = hospitals[0].to_dict()
            return jsonify(hospital_data)
    
    return redirect(url_for('error_page'), data=hospital_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))