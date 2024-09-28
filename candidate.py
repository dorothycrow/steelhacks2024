import requests
import wikipediaapi
from openai import OpenAI
from google.cloud import aiplatform
from google.oauth2 import service_account


FEC_API_KEY = ''
fec_base_url = 'https://api.open.fec.gov/v1/'
CIVIC_API_KEY = ''
OPENAI_API_KEY = '' 

# GCP_PROJECT = 'your-gcp-project-id'
# GCP_LOCATION = 'us-central1'  # Or your preferred region
# GCP_MODEL = 'models/text-bison-001'  # Replace with your PaLM 2 model

openai_client = OpenAI(api_key=OPENAI_API_KEY)


class Candidate:
    def __init__(self, name, cycle=2024):
        self.name = name
        self.cycle = cycle
        self.fec_data = None
        self.wiki_summary = None
        self.gpt_summary = None
        self.all_gpt_responses = []


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
            self.wiki_summary = page.text
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
            prompt_text = f"As an expert political analyst, provide a detailed summary of {self.name}'s policy positions based on the information below. Use only the information provided and avoid adding any unsupported claims or assumptions. For each policy area, include specific examples of policies, actions, or statements, and mention any major criticisms or controversies with relevant and specific details. Do not include information about positions or actions not mentioned in the provided text. If applicable, discuss any significant controversies related to criminal justice, law enforcement, or other areas where the candidate's past positions may conflict with their current policy stance. Include detailed examples of any contradictory actions, public statements, or specific events related to these controversies, but only if these are explicitly mentioned in the provided information:\n\n**1. Social Policy:** Outline key policies related to healthcare, education, civil rights, and other social issues. Include specific examples of {self.name}'s actions or statements and any major criticisms or controversies associated with these policies, particularly those related to criminal justice or law enforcement if relevant. Provide specific cases, laws, or incidents that highlight these criticisms only if they are included in the provided text.\n\n**2. Economic Policy:** Highlight significant policies related to taxation, job creation, economic growth, and fiscal management. Provide specific examples of policies or initiatives {self.name} has supported, along with notable criticisms or conflicting views. Mention specific economic events, legislative votes, or public statements that illustrate these policies and criticisms, but avoid adding information not found in the text.\n\n**3. Sustainability Policy:** Summarize the main policies related to environmental protection, renewable energy, and climate change. Include specific examples of {self.name}'s actions or initiatives and address any criticisms or contradictory positions with relevant details. Cite specific legislation, initiatives, or public statements that illustrate these criticisms, and provide detailed examples of any conflicts with past actions or policies, only if these are mentioned in the provided information.\n\nInformation: {self.wiki_summary}"
            self.prompt_gpt(prompt_text)
            """
            social_policy_prompt = f"As an expert political analyst, provide a detailed summary of {self.name}'s social policy positions based on the information below. Include both positive aspects and any criticisms or contradictions, and explain why people have these concerns. Use specific examples and historical context where applicable:\n\n{self.wiki_summary}"
            self.prompt_gpt(social_policy_prompt)
            self.all_gpt_responses.append(self.gpt_summary)
            
            economic_policy_prompt = f"As an expert political analyst, provide a detailed summary of {self.name}'s economic policy positions based on the information below. Include both positive aspects and any criticisms or contradictions, and explain why people have these concerns. Use specific examples and historical context where applicable:\n\n{self.wiki_summary}"
            self.prompt_gpt(economic_policy_prompt)
            self.all_gpt_responses.append(self.gpt_summary)
            
            sustainability_policy_prompt = f"As an expert political analyst, provide a detailed summary of {self.name}'s sustainability policy positions based on the information below. Include both positive aspects and any criticisms or contradictions, and explain why people have these concerns. Use specific examples and historical context where applicable:\n\n{self.wiki_summary}"
            self.prompt_gpt(sustainability_policy_prompt)
            self.all_gpt_responses.append(self.gpt_summary)
            """
        
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
        # for response in self.all_gpt_responses:
        #     print(response)
        


candidate_name = 'Kamala Harris'
candidate = Candidate(candidate_name)

candidate.fetch_fec_data()
candidate.fetch_wikipedia_summary()
candidate.generate_gpt_summary()
candidate.display_info()
