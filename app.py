from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g, flash
from models import db, User  # Import 'db' and 'User' from models
from bs4 import BeautifulSoup
#import axios
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from bs4 import BeautifulSoup
import time

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
            'location': f"{user.county}, {user.state}",
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
        
        # URL of the target website
        
        """
        url = "https://www.pavoterservices.pa.gov/Pages/voterregistrationstatus.aspx"
        payload = {
            'county': 'Allegheny',
            'zipcode': '15213',
            'first_name': 'Riya',
            'last_name': 'Shah',
            'dob': '09/03/2004'
        }

        with requests.Session() as session:
            response = session.post(url, data=payload)
            if response.status_code == 200:
                print("Form submitted successfully!")
                soup = BeautifulSoup(response.content, 'html.parser')
    
                # Print the entire HTML content of the page
                print("HTML Content of the Page:")
                print(soup.prettify())  # prettify() will format the HTML content for easier reading
                
                print("--------")
        
                status_element = soup.find(text="ACTIVE")
                
                if status_element:
                    print("Voter is ACTIVE.")
                    
                else:
                    print("Voter status not found.")
                    
            else:
                print("Failed to submit form", response.status_code)
            """
           
        """ 
        url = "https://www.sec.state.ma.us/voterregistrationsearch/myvoterregstatus.aspx"
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract hidden fields required for form submission
        viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
        eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']

        # Prepare payload with the user's data and hidden fields
        payload = {
            'ctl00$ContentPlaceHolder1$txtFirstName': 'Riya',
            'ctl00$ContentPlaceHolder1$txtLastName': 'Shah',
            'ctl00$ContentPlaceHolder1$ddlMonth': 'September',  # Select dropdown for month
            'ctl00$ContentPlaceHolder1$ddlDay': '3',  # Select dropdown for day
            'ctl00$ContentPlaceHolder1$ddlYear': '2004',  # Select dropdown for year
            'ctl00$ContentPlaceHolder1$txtZipCode': '01720',  # Zip code field
            'ctl00$ContentPlaceHolder1$chkboxIAgree': 'on',  # Checkbox to agree to the terms
            '__VIEWSTATE': viewstate,
            '__EVENTVALIDATION': eventvalidation,
            '__VIEWSTATEGENERATOR': viewstategenerator,
        }

        # Submit the form
        response = session.post(url, data=payload)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Process the response
        if "voter status" in soup.text.lower():
            print("Voter registration status found.")
        else:
            print("No voter registration status found.")
            
        """
        
        

        driver = webdriver.Chrome()  # Ensure you have the correct driver installed
        driver.get("https://www.sec.state.ma.us/voterregistrationsearch/myvoterregstatus.aspx")
        
        # Fill out form fields
        driver.find_element(By.ID, "MainContent_txtFirstName").send_keys("Riya")
        driver.find_element(By.ID, "MainContent_txtLastName").send_keys("Shah")
        
        # Select Month
        Select(driver.find_element(By.ID, "MainContent_ddlMonth")).select_by_value('9')  # September
        
        # Select Day
        Select(driver.find_element(By.ID, "MainContent_ddlDay")).select_by_value('3')
        
        # Select Year
        Select(driver.find_element(By.ID, "MainContent_ddlYear")).select_by_value('2004')
        
        # Fill out Zip Code
        driver.find_element(By.ID, "MainContent_txtZip").send_keys("01720")
        
        # Agree to the terms
        driver.find_element(By.ID, "MainContent_chkUnderstand").click()
        
        # Submit the form
        driver.find_element(By.ID, "MainContent_btnSearch").click()
        
        # Wait for the response to load
        time.sleep(3)  # You might need to adjust this wait time based on page load time
        
        # Get the response
        page_source = driver.page_source
        driver.quit()
        
        # Parse the result with BeautifulSoup (optional)
        soup = BeautifulSoup(page_source, 'html.parser')
        # print(soup.prettify())

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

@app.route('/update_game_badge', methods=['POST'])
def update_game_badge():
    last_user = User.query.order_by(User.id.desc()).first()  # Get the last user
    if last_user:
        last_user.gameBadge = True
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'User not found'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)