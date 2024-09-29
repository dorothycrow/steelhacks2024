import requests
import wikipediaapi
from openai import OpenAI
import google.generativeai as genai

# Replace with your actual API keys
FEC_API_KEY = 'URR0BmDklHS6hZZUuxUY9Kp4o54fcHA6Itw1emrE'
fec_base_url = 'https://api.open.fec.gov/v1/'
GEMINI_API_KEY = 'AIzaSyBmIDBw3-xMslVnA-hgyGlrqxj_EbSv2io'
OPENAI_API_KEY = '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'

class Candidate:
    def __init__(self, name, cycle=2024):
        self.name = name
        self.cycle = cycle
        self.fec_data = None
        self.wiki_summary = None
        self.gemini_response = None
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")

    def fetch_fec_data(self):
        params = {
            'api_key': FEC_API_KEY,
            'name': self.name,
            'cycle': self.cycle
        }
        response = requests.get(f'{fec_base_url}candidates/search/', params=params)
        if response.status_code == 200:
            self.fec_data = response.json()
        else:
            self.fec_data = None

    def fetch_wikipedia_summary(self):
        wiki_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='VoterUp - SteelHacks Fall 2024 (vad50@pitt.edu)'
        )
        page = wiki_wiki.page(self.name)
        if page.exists():
            self.wiki_summary = page.text
        else:
            self.wiki_summary = f"Wikipedia page for {self.name} does not exist."

    def generate_gemini_summary(self):
        if self.wiki_summary:
            prompt_text = f"As an expert political analyst, provide a detailed summary of {self.name}'s policy positions based on the information below. Information: {self.wiki_summary}"
            self.gemini_response = self.gemini_model.generate_content(prompt_text)
        else:
            self.gemini_response = "No Wikipedia summary available to generate summary."


