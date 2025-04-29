import os
import numpy as np
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

# Constants for Google API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'path/to/service_account.json'  # Path to the service account JSON file
SPREADSHEET_ID = 'your_google_form_spreadsheet_id'  # Google Sheets ID
CALENDAR_ID = 'your_google_calendar_id'  # Google Calendar ID

# Google API setup
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)
calendar_service = build('calendar', 'v3', credentials=credentials)

# Fetch data from Google Forms
def fetch_google_form_data():
    """
    Fetches data from a Google Form linked to a Google Sheet.
    Returns the data as a pandas DataFrame.
    """
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Form Responses 1').execute()
    values = result.get('values', [])
    if not values:
        raise ValueError("No data found in the Google Form.")
    headers = values[0]
    data = pd.DataFrame(values[1:], columns=headers)
    return data

# Fetch prayer services and sermonettes from Google Calendar
def fetch_google_calendar_events():
    """
    Fetches events from Google Calendar and categorizes them as prayer services or sermonettes.
    Returns two lists: prayer_services and sermonettes.
    """
    events_result = calendar_service.events().list(calendarId=CALENDAR_ID, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    prayer_services = []
    sermonettes = []
    for event in events:
        if 'Prayer Service' in event.get('summary', ''):
            prayer_services.append(event['start']['date'])
        elif 'Sermonette' in event.get('summary', ''):
            sermonettes.append(event['start']['date'])
    return prayer_services, sermonettes

# Prepare survey data
def prepare_survey_data(data):
    """
    Prepares survey data by renaming columns, setting the index, and converting Yes/No values to boolean.
    """
    data.columns = ['Timestamp', 'Name', 'Email', 'Phone', 'Role', 'Zions Harp', 'Gospel Hymns', 'Hymns of Zion',
                    'Celebration Hymnal', 'Junior Hymnal', 'Camp Book', 'Dates off', 'Capacity', 'Weekly preference']
    data.set_index("Name", inplace=True)
    for column in data.columns:
        data[column] = data[column].map(lambda x: True if x == 'Yes' else (False if x == 'No' else x))
    return data

# Prepare decision tree data
def prepare_decision_tree_data(survey_df, leader_list, pianist_list):
    """
    Prepares data for training a decision tree classifier.
    Returns the training data and labels.
    """
    data = []
    labels = []
    for name in survey_df.index:
        for subject in survey_df.columns:
            if subject not in ['Dates off', 'Weekly preference', 'Capacity', 'Role']:
                continue
            for date in pd.date_range('2024-05-01', periods=120):
                weekday = date.weekday()
                start_time = '7:30:00 PM' if weekday == 2 else '5:15:00 PM'
                is_leader = name in leader_list
                is_pianist = name in pianist_list
                is_available = str(date)[:10] not in Convert(survey_df.loc[name, 'Dates off'])
                prefers_time = start_time in Convert(survey_df.loc[name, 'Weekly preference'])
                plays_subject = survey_df.loc[name, subject]
                data.append([name, subject, weekday, start_time, is_leader, is_pianist, is_available, prefers_time, plays_subject])
                labels.append(1 if is_leader or is_pianist else 0)
    return data, labels

# Train decision tree
def train_decision_tree(data, labels):
    """
    Trains a decision tree classifier using the provided data and labels.
    Returns the trained classifier and a label encoder.
    """
    le = LabelEncoder()
    data_encoded = [le.fit_transform(col) for col in zip(*data)]
    clf = DecisionTreeClassifier()
    clf.fit(list(zip(*data_encoded)), labels)
    return clf, le

# Decision tree-based selection
def select_person(row, role_list, survey_df, previous_people, clf, le):
    """
    Selects a person for a role (leader or pianist) using a decision tree classifier.
    Ensures the person meets all criteria.
    """
    candidates = []
    for person in role_list:
        weekday = row['Start Date'].weekday()
        start_time = row['Start Time']
        is_available = str(row['Start Date'])[:10] not in Convert(survey_df.loc[person, 'Dates off'])
        prefers_time = start_time in Convert(survey_df.loc[person, 'Weekly preference'])
        plays_subject = survey_df.loc[person, row['Subject']]
        if all([is_available, prefers_time, plays_subject, person not in previous_people]):
            candidates.append(person)
    if not candidates:
        return None
    candidate_data = [[person, row['Subject'], weekday, start_time, person in role_list, True, True, True, True] for person in candidates]
    candidate_data_encoded = [le.transform(col) for col in zip(*candidate_data)]
    predictions = clf.predict(list(zip(*candidate_data_encoded)))
    for i, prediction in enumerate(predictions):
        if prediction == 1:
            return candidates[i]
    return None

# Fill schedule
def fill_schedule(df, leader_list, pianist_list, survey_df, prayer_services, sermonettes, clf, le):
    """
    Fills the schedule DataFrame with leaders and pianists based on availability and preferences.
    Updates the schedule with prayer services and sermonettes.
    """
    previous_leaders = []
    previous_pianists = []
    for index, row in df.iterrows():
        leader = select_person(row, leader_list, survey_df, previous_leaders, clf, le)
        pianist = select_person(row, pianist_list, survey_df, previous_pianists, clf, le)
        if leader:
            df.at[index, 'Leader'] = leader
            previous_leaders.append(leader)
            if len(previous_leaders) > 3:
                previous_leaders.pop(0)
        if pianist:
            df.at[index, 'Pianist'] = pianist
            previous_pianists.append(pianist)
            if len(previous_pianists) > 3:
                previous_pianists.pop(0)
        if str(row['Start Date'])[:10] in prayer_services:
            df.at[index, 'Subject'] = "Prayer Service"
        elif str(row['Start Date'])[:10] in sermonettes:
            df.at[index, 'Subject'] = "Sermonette"

# Create Google Calendar events
def create_google_calendar_events(schedule_df):
    """
    Creates events in Google Calendar based on the schedule DataFrame.
    """
    for _, row in schedule_df.iterrows():
        event = {
            'summary': row['Subject'],
            'description': f"Leader: {row['Leader']}, Pianist: {row['Pianist']}",
            'start': {'dateTime': f"{row['Start Date']}T{row['Start Time']}", 'timeZone': 'UTC'},
            'end': {'dateTime': f"{row['End Date']}T{row['End Time']}", 'timeZone': 'UTC'},
        }
        calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

# Main function
def main():
    """
    Main function to fetch data, process the schedule, and upload it to Google Calendar.
    """
    # Fetch data
    form_data = fetch_google_form_data()
    prayer_services, sermonettes = fetch_google_calendar_events()
    
    # Prepare data
    survey_df = prepare_survey_data(form_data)
    leader_list, pianist_list = [], []  # Populate based on survey_df
    data, labels = prepare_decision_tree_data(survey_df, leader_list, pianist_list)
    clf, le = train_decision_tree(data, labels)
    
    # Generate schedule
    df = pd.DataFrame({'Start Date': pd.date_range('2024-05-01', periods=120), 'End Date': pd.date_range('2024-05-01', periods=120)})
    df['Start Time'] = '7:30:00 PM'
    df['End Time'] = '7:55:00 PM'
    df['Subject'] = 'Zions Harp'
    df['Leader'] = ''
    df['Pianist'] = ''
    fill_schedule(df, leader_list, pianist_list, survey_df, prayer_services, sermonettes, clf, le)
    
    # Export schedule
    df.to_csv('Music_Schedule.csv')
    create_google_calendar_events(df)
    print("Schedule created and uploaded to Google Calendar.")

if __name__ == "__main__":
    main()