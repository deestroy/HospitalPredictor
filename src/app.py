import os
import time
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    return render_template('temp.html', maps_api_key=maps_api_key)


# 404 page
@app.route('/404')  
def error_page():
    return render_template('404.html')


# update hospital data
@app.route('/update-hospital-data', methods = ['POST'])
def update_hospital_data():
    
    if request.method == 'POST':
        try:
            data = request.get_json()

            # if health care worker: get hospital and get rating
            # if general public and been to hospital: get hospital and get rating
            # if covid: get postal code
            
            questions = data['form_response']['definition']['fields']
            answers = data['form_response']['answers']

            qa_pairs = {}

            for q, a in zip(questions, answers):
                qa_pairs[q['title']] = [a[a['type']]]

            scale, postal_code = -1, -1

            # health care worker
            if qa_pairs['Which best descibes you']['label'] == 'Health Care Worker':
                hospital = qa_pairs['Which hospital do you work at']['label']
                rating = qa_pairs['On a scale of 1 to 10, how would you describe the current situation at your hospital?']
                scale = 2

            # general public
            elif qa_pairs['Have you been in a hospital in the last 24 hours']['label'] == 'Yes':
                hospital = qa_pairs['Which hospital are you at / have you visited?']['label']
                rating = qa_pairs['On a scale of 1 to 10, how would you describe the current situation at your hospital?']
                scale = 1

            # has covid
            # WHAT TO DO WITH THIS DATA?
            if qa_pairs['Do you have COVID-19']['label'] == 'Yes' and 'What is your Postal Code' in qa_pairs:
                postal_code = qa_pairs['What is your Postal Code']


            # update occupancy field
            if scale > 0 and hospital != 'Other':
                h = db.collection(u'hospitals').document(hospital).to_dict()
                num_responses = h['num_responses']
                curr_occupancy = max(0, h['percent_occupancy'])
                updated_occupancy = int((curr_occupancy + rating*10*scale) / (num_responses + scale))
                db.collection(u'hospitals').document(hospital).update({u'num_responses': num_responses+1, u'percent_occupancy': updated_occupancy})

            # FOR TESTING PURPOSES
            elif scale > 0 and hospital == 'Other':
                h = db.collection(u'ontario_cases').document(hospital).to_dict()
                num_responses = h['num_responses']
                curr_occupancy = max(0, h['percent_occupancy'])
                updated_occupancy = int((curr_occupancy + rating*10*scale) / (num_responses + scale))
                db.collection(u'ontario_cases').document(u'0').update({u'num_responses': num_responses+1, u'percent_occupancy': updated_occupancy})

            return jsonify({'Success':True}), 200
        
        except:
            return jsonify({'Error': 'Something went wrong'})
    
    return jsonify({'Error': 'Bad Request (expected POST)'}), 400


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