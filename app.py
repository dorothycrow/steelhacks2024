from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import yaml
import requests
import os

from models import db, User



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.root_path, "voter.db")
db = SQLAlchemy(app)
#app.config.from_object('config.Config')

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

#initilizes data base
@app.cli.command("initdb") 
def initdb_command():
    db.create_all()
    print("Initialized the database.")
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    username = request.form['username']
    state = request.form['state']
    county = request.form['county']
    location = request.form['location']
    # Process the sign-up (e.g., save to a database)

    # Redirect to the elections page with the location as a query parameter
    return redirect(url_for('elections', location=location))

@app.route('/elections')
def elections():
    location = request.args.get('location')
    elections = get_upcoming_elections(location)
    return render_template('elections.html', elections=elections)

def get_upcoming_elections(location):
    # Replace with your actual API endpoint
    api_url = f"https://api.example.com/elections?location={location}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Assuming the response is in JSON format
    except requests.RequestException as e:
        print(f"Error fetching elections: {e}")
        return []  # Return an empty list if there's an error

@app.route('/election/<int:election_id>')
def election_detail(election_id):
    # Fetch election details based on election_id (you may need to adjust this)
    # For demonstration, let's use a mock detail
    election = {'id': election_id, 'name': f'Election {election_id}', 'date': '2024-11-01', 'details': 'Details about the election.'}
    return render_template('election_detail.html', election=election)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)
