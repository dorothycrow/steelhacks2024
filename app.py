from flask import Flask, render_template, request, redirect, url_for
import yaml
import requests

app = Flask(__name__)
app.config.from_object('config.Config')

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    username = request.form['username']
    password = request.form['password']
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)
