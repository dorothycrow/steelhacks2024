import requests
import wikipediaapi
from openai import OpenAI


FEC_API_KEY = ''
fec_base_url = 'https://api.open.fec.gov/v1/'
CIVIC_API_KEY = ''
OPENAI_API_KEY = ''

openai_client = OpenAI(api_key=OPENAI_API_KEY)


class Candidate:
    def __init__(self, name, cycle=2024):
        self.name = name
        self.cycle = cycle
        self.fec_data = None
        self.wiki_summary = None
        self.gpt_summary = None


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
            print(f'Error: {response.status_code}')
            self.fec_data = None


    def fetch_wikipedia_summary(self):
        wiki_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='VoterUp - SteelHacks Fall 2024 (vad50@pitt.edu)'
        )
        page = wiki_wiki.page(self.name)
        if page.exists():
            self.wiki_summary = page.summary
        else:
            self.wiki_summary = f"Wikipedia page for {self.name} does not exist."


    def prompt_gpt(self, prompt):
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        self.gpt_summary = response.choices[0].message.content


    def generate_gpt_summary(self):
        if self.wiki_summary:
            prompt_text = f"Summarize the policies supported by {self.name} based on this information: {self.wiki_summary}"
            self.prompt_gpt(prompt_text)
        else:
            self.gpt_summary = "No Wikipedia summary available to generate GPT summary."


    def display_info(self):
        # print(f"Candidate Name: {self.name}")
        # print("\nFEC Data:")
        # print(self.fec_data)
        # print("\nWikipedia Summary:")
        # print(self.wiki_summary)
        print("\nGPT-3 Summary:")
        print(self.gpt_summary)


candidate_name = 'Kamala Harris'
candidate = Candidate(candidate_name)

candidate.fetch_fec_data()
candidate.fetch_wikipedia_summary()
candidate.generate_gpt_summary()
candidate.display_info()
