# temporary mapping algorithm of existing Canadian cases data to hospital occupancy rates

import json
import geocoder
import os
from dotenv import load_dotenv
import pandas as pd
from math import inf
from math import sin
from math import cos
from math import atan2
from math import sqrt

# firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# load environment variables
dotenv_path = '.env'
load_dotenv(dotenv_path)

# firebase setup
cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# google maps api key
maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')


# flag to only activate a specific part of the script
part = 0


# ----- PART 1 -----
# create json file with regions and latlng and number of cases
if part == 1:

    # lookup table of already known lat-lngs for each region (and counter for number of cases in that region)
    # so I don't have to redo these geocoder calls
    health_regions = {
        'Toronto' : {'cases': 0, 'hospitals': [], 'location': [43.653226, -79.3831843]},
        'Vancouver Coastal' : {'cases': 0, 'hospitals': [], 'location': [49.2827291, -123.1207375]},
        'Middlesex-London' : {'cases': 0, 'hospitals': [], 'location': [42.9849233, -81.2452768]},
        'Interior' : {'cases': 0, 'hospitals': [], 'location': [49.2835277, -123.1169394]},
        'Fraser' : {'cases': 0, 'hospitals': [], 'location': [59.71711500000001, -135.049219]},
        'Montréal' : {'cases': 0, 'hospitals': [], 'location': [45.5016889, -73.567256]},
        'York' : {'cases': 0, 'hospitals': [], 'location': [43.6956787, -79.4503544]},
        'Durham' : {'cases': 0, 'hospitals': [], 'location': [44.1763254, -80.8185006]},
        'Laurentides' : {'cases': 0, 'hospitals': [], 'location': [46.6181619, -75.01814929999999]},
        'Waterloo' : {'cases': 0, 'hospitals': [], 'location': [43.4642578, -80.5204096]},
        'Peel' : {'cases': 0, 'hospitals': [], 'location': [43.6766398, -79.7848422]},
        'Calgary' : {'cases': 0, 'hospitals': [], 'location': [51.04473309999999, -114.0718831]},
        'Montérégie' : {'cases': 0, 'hospitals': [], 'location': [45.3290251, -72.81482489999999]},
        'Edmonton' : {'cases': 0, 'hospitals': [], 'location': [53.5461245, -113.4938229]},
        'Sudbury' : {'cases': 0, 'hospitals': [], 'location': [46.4917317, -80.99302899999999]},
        'Ottawa' : {'cases': 0, 'hospitals': [], 'location': [45.4215296, -75.69719309999999]},
        'Halton' : {'cases': 0, 'hospitals': [], 'location': [43.53253720000001, -79.87448359999999]},
        'Mauricie' : {'cases': 0, 'hospitals': [], 'location': [46.6629657, -72.8512198]},
        'Island' : {'cases': 0, 'hospitals': [], 'location': [50.39297269999999, -125.1186076]},
        'Hamilton' : {'cases': 0, 'hospitals': [], 'location': [43.2557206, -79.8711024]},
        'Simcoe Muskoka' : {'cases': 0, 'hospitals': [], 'location': [44.4716525, -79.8296743]},
        'Saskatoon' : {'cases': 0, 'hospitals': [], 'location': [52.1332144, -106.6700458]},
        'Winnipeg' : {'cases': 0, 'hospitals': [], 'location': [49.895136, -97.13837439999999]},
        'Chaudière-Appalaches' : {'cases': 0, 'hospitals': [], 'location': [46.6981917, -71.2993195]},
        'Estrie' : {'cases': 0, 'hospitals': [], 'location': [45.7903568, -70.9565703]},
        'Zone 1 (Moncton area)' : {'cases': 0, 'hospitals': [], 'location': [46.0878165, -64.7782313]},
        'Niagara' : {'cases': 0, 'hospitals': [], 'location': [43.0581645, -79.29021329999999]},
        'Haliburton Kawartha Pineridge' : {'cases': 0, 'hospitals': [], 'location': [43.9683674, -78.2856082]},
        'Huron Perth' : {'cases': 0, 'hospitals': [], 'location': [43.6416566, -81.6911559]},
        'Northwestern' : {'cases': 0, 'hospitals': [], 'location': [64.8255441, -124.8457334]},
        'Eastern' : {'cases': 0, 'hospitals': [], 'location': [43.6668105, -79.6419657]},
        'Lanaudière' : {'cases': 0, 'hospitals': [], 'location': [46.1256124, -73.704151]},
        'Estrie' : {'cases': 0, 'hospitals': [], 'location': [45.7903568, -70.9565703]},
        'Prince Edward Island' : {'cases': 0, 'hospitals': [], 'location': [46.510712, -63.41681359999999]}
    }

    data_xl = pd.read_excel(r'data/cases.xlsx')
    df = pd.DataFrame(data_xl, columns=['case_id', 'health_region', 'province'])

    for case_id, region, prov in zip(df['case_id'], df['health_region'], df['province']):
        try:
            # insert new region into lookup table
            if region not in health_regions.keys():
                g = geocoder.google(region + ' ' + prov + ' Canada', key=maps_api_key)
                health_regions[region] =  {'cases': 0, 'location': g.latlng}
            
            # increment # cases for that region
            health_regions[region]['cases'] += 1

            print(case_id)
        
        except:
            print('----- ERROR with case ID: {} -----'.format(case_id))

    # some error trapping
    if 'Not Reported' in health_regions:
        del health_regions['Not Reported']

    json_obj = json.dumps(health_regions, indent=4, sort_keys=True)
    with open('data/health_regions_data.json', 'w') as file:
        file.write(json_obj)


# ----- PART 2 -----
# add list of hospitals to regions
elif part == 2:

    with open('data/health_regions_data.json', 'r') as file:
        health_regions = json.load(file)
    
    # get latlngs of each hospital
    db_data = db.collection(u'hospitals').stream()
    hospitals = {}

    for hospital in db_data:
        hospital = hospital.to_dict()
        hospitals[hospital['name']] = [hospital['lat'], hospital['lng']]
        print(hospital['name'])
    
    # for each hospital, find closest region
    for hospital, location in hospitals.items():
        min_dist = inf
        min_region = 'ERROR'
        lat1 = location[0]
        lng1 = location[1]

        for region, val in health_regions.items():
            lat2 = val['location'][0]
            lng2 = val['location'][1]

            # use Haversine Formula to caclulate great circle distance between two points
            dlng = lng2 - lng1
            dlat = lat2 - lat1
            a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlng/2))**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))

            if c < min_dist:
                min_dist, min_region = c, region
    
        # add hospital to regions data
        if 'hospitals' in health_regions[min_region]:
            health_regions[min_region]['hospitals'].append(hospital)
        else:
            health_regions[min_region]['hospitals'] = [hospital]
    
    json_obj = json.dumps(health_regions, indent=4, sort_keys=True)
    with open('data/health_regions_data.json', 'w') as file:
        file.write(json_obj)


# ----- PART 3 -----
# determine occupancy for each hospital
elif part == 3:
    db_data = db.collection(u'hospitals').stream()
    hospitals = {}

    # create a table to keep track of hospital bed data
    # IMPORTANT: it is assumed that num_beds is greater than zero
    for hospital in db_data:
        hospital = hospital.to_dict()
        hospitals[hospital['name']] = {'beds_occupied': 0, 'total_beds': int(hospital['num_beds'])}
        print(hospital['name'])
        
    with open('data/health_regions_data.json', 'r') as file:
        health_regions = json.load(file)

    print('\nGoing through each region:\n')

    # for each region, keep assigning cases to hospitals until no more cases or hospital is full
    for region, val in health_regions.items():
        try:
            queue = val['hospitals']
            cases = val['cases']
            i = 0

            while len(queue) > 0 and cases > 0:
                hospital = queue[i]

                # if hospital still has empty beds, assign it a case
                if hospitals[hospital]['beds_occupied'] < hospitals[hospital]['total_beds']:
                    hospitals[hospital]['beds_occupied'] += 1
                    cases -= 1
                
                    # if hospital is full, remove it from the queue
                    if hospitals[hospital]['beds_occupied'] == hospitals[hospital]['total_beds']:
                        del queue[i]
                    else:
                        i += 1
                
                if i >= len(queue):
                    i = 0
            
            print(region)
            
        except:
            print('----- ERROR with ' + region + ' -----')
    
    # for each hospital, set its occupancy to beds occupied / total beds
    for val in hospitals.values():
        val['occupancy'] = round(100 * val['beds_occupied'] / val['total_beds'])
    
    # store in json
    json_obj = json.dumps(hospitals, indent=4, sort_keys=True)
    with open('data/hospital_occupancy_estimates.json', 'w') as file:
        file.write(json_obj)


# ----- PART 4 -----
# update db data
elif part == 4:

    with open('data/hospital_occupancy_estimates.json', 'r') as file:
        estimates = json.load(file)

    for name, val in estimates.items():
        try:
            db.collection(u'hospitals').document(name).update({u'percent_occupancy': val['occupancy']})
            print(name)
        except:
            print('----- ERROR with ' + name + ' -----')