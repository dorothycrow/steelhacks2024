from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g, flash
from models import db, User  # Import 'db' and 'User' from models
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import yaml
import requests
from candidate import Candidate

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.root_path, "voter.db")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(app.root_path, "voter2.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
            'location': f"{user.county}, {user.state}",
            'registered': user.registered,
            'gameBadge': user.gameBadge
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
        
        dob_parts = new_user.dob.split("-")  #MM-DD-YYYY
        month = dob_parts[0]
        day = dob_parts[1]
        year = dob_parts[2]
        
        driver = webdriver.Chrome()
        driver.get("https://www.sec.state.ma.us/voterregistrationsearch/myvoterregstatus.aspx")
        
        driver.find_element(By.ID, "MainContent_txtFirstName").send_keys(new_user.fName)
        driver.find_element(By.ID, "MainContent_txtLastName").send_keys(new_user.lName)
        
        Select(driver.find_element(By.ID, "MainContent_ddlMonth")).select_by_value(str(int(month)))
        Select(driver.find_element(By.ID, "MainContent_ddlDay")).select_by_value(day.lstrip('0'))
        Select(driver.find_element(By.ID, "MainContent_ddlYear")).select_by_value(year)
        
        driver.find_element(By.ID, "MainContent_txtZip").send_keys(new_user.zipcode)
        driver.find_element(By.ID, "MainContent_chkUnderstand").click()
        driver.find_element(By.ID, "MainContent_btnSearch").click()

        time.sleep(3)

        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        
        if "Voting Status:\nActive" in soup.text:
            new_user.registered = True
            db.session.commit()
            return redirect(url_for('elections'))
        else:
            return redirect(url_for('register'))
            
    return redirect(url_for('elections'))


@app.route('/register')
def register():
    election = get_upcoming_elections()
    election = election.get('state')
    election_body = election[0]['electionAdministrationBody']
    return render_template('register.html', election_body=election_body)

@app.route('/elections')
def elections():
    election = get_upcoming_elections()
    election_info = election.get('election')
    return render_template('elections.html', election_info=election_info)


@app.route('/login')
def login():
    return render_template('login.html')


def get_upcoming_elections():
    #put api key
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
        return [
            {'id': 1, 'name': 'Mock Election 1', 'date': '2024-11-01'},
            {'id': 2, 'name': 'Mock Election 2', 'date': '2024-12-15'},
        ]

#@app.route('/election/<int:election_id>')
#def election_detail(election_id):
    # Fetch election details based on election_id (you may need to adjust this)
    # For demonstration, let's use a mock detail
    #election = {'id': election_id, 'name': f'Election {election_id}', 'date': '2024-11-01', 'details': 'Details about the election.'}
    #return render_template('election_detail.html', election=election)

@app.route('/elections/game')
def game():
    return render_template('game.html')

@app.route('/update_game_badge', methods=['POST'])
def update_game_badge():
    last_user = User.query.order_by(User.id.desc()).first()  # Get the last user
    if last_user:
        last_user.gameBadge = True
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/candidates')
def candidates():
    # Create candidate instances
    candidates = [Candidate('Kamala Harris'), Candidate('Donald Trump')]

    # Fetch data for each candidate
    for candidate in candidates:
        candidate.fetch_fec_data()
        #candidate.fetch_wikipedia_summary()
        candidate.generate_gemini_summary()

    # Render the comparison HTML
    return render_template('candidates.html', candidates=candidates)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)