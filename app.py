from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g, flash
from models import db, User  # Import 'db' and 'User' from models
from bs4 import BeautifulSoup
#import axios

import yaml
import requests
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.root_path, "voter.db")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.root_path, "voter2.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Create tables if not already created (optional, can use migrations instead)
with app.app_context():
    db.create_all()

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

@app.cli.command("initdb") 
def initdb_command():
    with app.app_context():
        db.create_all()
        print("Initialized the database.")

def get_user_by_id(user_id):
    """Convenience method to look up the user for an id."""
    rv = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return rv

@app.before_request
def before_request():
    g.user = None
    if "user_id" in session:
        g.user = db.session.execute(db.select(User).where(User.id == session["user_id"])).scalar()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user_profile')
def user_profile():
    user = User.query.order_by(User.id.desc()).first()  # Get the last user added
    if user:
        user_info = {
            'username': f"{user.fName} {user.lName}",
            'location': f"{user.county}, {user.state}"
        }
        return render_template('user_profile.html', user=user_info)
    else:
        return "No users found", 404

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/submit_signup', methods=['GET', 'POST'])
def submit_signup():
    if g.user:
        return redirect(url_for("/elections"))
    error = None
    if request.method == "POST":
        new_user = User(
            request.form["firstName"],
            request.form["lastName"],
            request.form["address"],
            request.form["city"],
            request.form["state"],
            request.form["county"],
            request.form["zip"],
            request.form["dob"],
            registered=False,
            gameBadge=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # URL of the target website
        url = 'https://www.pavoterservices.pa.gov/Pages/voterregistrationstatus.aspx'
        
        # Create a session to persist parameters across requests
        with requests.Session() as session:
            response = session.post(url, data={
                'county': new_user.county,
                'zipcode': new_user.zipcode,
                'first_name': new_user.fName,
                'last_name': new_user.lName,
                'dob': new_user.dob,
                'address': new_user.address,
                'city': new_user.city
            })
        
        # Parse the response
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            voter_status = soup.find('div', class_='voter-status')  # Update selector as needed
            if voter_status:
                new_user.registered = True
                db.session.commit()
                return jsonify({'status': 'success', 'voter_status': voter_status.text.strip()})
            else:
                new_user.registered = False
                db.session.commit()
                #return jsonify({'status': 'error', 'message': 'Voter status not found'})
                return redirect(url_for('register'))  # Redirect to the new page
        else:
            return jsonify({'status': 'error', 'message': 'Failed to retrieve information'})

    return redirect(url_for('elections'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/elections')
def elections():
    elections = get_upcoming_elections()
    return render_template('elections.html', elections=elections)


@app.route('/login')
def login():
    return render_template('login.html')


def get_upcoming_elections():
    # Replace with your actual API endpoint
    API_KEY = 'AIzaSyBOx-4M4gD-2KcQZkHqP0wVEfHOqVrv4nY'
    user = User.query.order_by(User.id.desc()).first()  # Get the last user added
    address = user.address + ' ' + user.city + ' ' + user.state
    #election_id = 9000
    api_url = f"https://www.googleapis.com/civicinfo/v2/voterinfo?key={API_KEY}&address={address}&electionId=9000"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Assuming the response is in JSON format
    except requests.RequestException as e:
        print(f"Error fetching elections: {e}")
        # Return a mock list of elections
        return [
            {'id': 1, 'name': 'Mock Election 1', 'date': '2024-11-01'},
            {'id': 2, 'name': 'Mock Election 2', 'date': '2024-12-15'},
        ]  # Example mock elections

#@app.route('/election/<int:election_id>')
#def election_detail(election_id):
    # Fetch election details based on election_id (you may need to adjust this)
    # For demonstration, let's use a mock detail
    #election = {'id': election_id, 'name': f'Election {election_id}', 'date': '2024-11-01', 'details': 'Details about the election.'}
    #return render_template('election_detail.html', election=election)

@app.route('/elections/game')
def game():
    return render_template('game.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)
