import os
import time
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# load environment variables
dotenv_path = '.env'
load_dotenv(dotenv_path)

# initialize flask application
app = Flask(__name__)

# firebase setup
cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app()
db = firestore.client()

def format_server_time():
  server_time = time.localtime()
  return time.strftime("%I:%M:%S %p", server_time)

# main page
@app.route('/')
def index():
    context = { 'server_time': format_server_time() }
    return render_template('index.html', context=context)


# update existing hospital with new data (all fields)
@app.route('/add-hospital-data', methods = ['POST'])
def add_hospital_data():
    req_data = request.get_json()
    name = req_data['name']

    db.collection(u'hospitals').document(name).set(req_data.to_dict())
    return 'Sucessfully added hospital data'


# returns data for specified hospital
@app.route('/get-hospital-data', methods = ['POST'])
def get_hospital_data():
    name = request.form['name']

    docs = db.collection(u'hospitals').where(u'name', u'==', name).stream()
    
    # if requested hospital is not in the database
    if len(docs) == 0:
        return redirect(url_for('404'))
    
    hospital_data = docs[0].to_dict()
    return jsonify(hospital_data)


@app.route('/404')
def error_page():
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))