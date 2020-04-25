import os
import time
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# load environment variables
dotenv_path = '.env'
load_dotenv(dotenv_path)

# initialize flask application
app = Flask(__name__, static_folder='static')

# firebase setup
cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# google maps api key
maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

# db cache
data = None


# main page
@app.route('/')
def index():
    return render_template('index.html')


# 404 page
@app.route('/404')  
def error_page():
    return render_template('404.html')


# data form page
@app.route('/data-form')
def data_form():
    return render_template('data_form.html')


# map page
@app.route('/map')
def map():
    return render_template('map.html', maps_api_key=maps_api_key)


# add new hospital data (all fields)
@app.route('/add-hospital-data', methods = ['POST'])
def add_hospital_data():

    if request.method == 'POST':
        req_data = request.form
        hospital = {
            'name': req_data.get('name'), 
            'address': req_data.get('address'), 
            'city': req_data.get('city'), 
            'country': req_data.get('country'),
            'health_region': req_data.get('health_region'),
            'lat': req_data.get('lat'),
            'lng': req_data.get('lng'),
            'num_beds': req_data.get('num_beds'), 
            'percent_occupancy': req_data.get('percent_occupancy'),
            'postal_code': req_data.get('postal_code'),
            'province': req_data.get('province')
        }
        db.collection(u'hospitals').document(req_data['name']).set(hospital)
        return redirect(url_for('index'))
    
    return redirect(url_for('error_page'))


# get all hospital data from database
@app.route('/get-hospital-data', methods = ['GET'])
def get_hospital_data():

    if request.method == 'GET':
        global data
        if data is None: 
            print('Performed db query')
            data = db_query()
        return json.dumps(data)

    return redirect(url_for('error_page'))


# retrieve data from db
def db_query():
    hospitals = db.collection('hospitals').stream()  
    cases = db.collection('canada_cases').stream()
    
    data = {'hospitals': [], 'canada_cases': []}
    for hospital in hospitals:
        data['hospitals'].append(hospital.to_dict())
    for case in cases:
        case = case.to_dict()['cases']
        for i in range(0, len(case), 2):
            data['canada_cases'].append([case[i], case[i+1]])
    return data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
