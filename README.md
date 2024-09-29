# README

## VoterUp Overview

This web application helps users navigate the voting process in their state by providing personalized resources based on their location and registration status. Users can check their registration, find polling locations, vote absentee, track their ballots, and explore upcoming elections with detailed candidate information.

## Features

- **User Registration**: Users can input their personal and location-related information, which is securely stored in an SQL database.
  
- **Registration Check**: The application automatically verifies if the user is registered to vote in their state. (this is currently only set up for MA)
  
- **Voting Resources**: If the user is not registered, the app provides tailored resources for:
  - Registering to vote
  - Finding polling locations
  - Voting absentee
  - Tracking their ballot
  
- **Election Countdown**: Displays a list of upcoming elections in the user's area with a countdown timer.
  
- **Candidate Information**: Users can click on an election to view information about the candidates and their policy differences.
  
- **Trivia Games and Badges**: Engage users with trivia games related to voting, where they can earn badges for successful completion.

## Usage

1. Clone the repository
2. Install requirements.txt
3. Add your own API Keys for Google Civic Information API and Gemini API
