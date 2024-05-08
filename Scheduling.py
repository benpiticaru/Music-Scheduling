import numpy as np
import pandas as pd
from datetime import date
import calendar
from itertools import cycle, islice
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input_file", default="C:/Users/Benjamin Piticaru/Downloads/January - April Leading survey (Responses) - Form Responses 1 (3).csv")
parser.add_argument("-o", "--output_folder", default="C:/Users/Benjamin Piticaru/Documents/python projects/Music_Scheduling")
parser.add_argument("-s", "--start_month", default="2024-05-01")
parser.add_argument("-p", "--prayer_services",default="2024-07-10")
parser.add_argument("-n", "--sermonettes",default="2024-07-31,2024-08-21")

args = parser.parse_args()

address = args.input_file
output = args.output_folder
begin_date = args.start_month
prayer_services = args.prayer_services
sermonettes = args.sermonettes

survey_df = pd.read_csv(address)
survey_df = survey_df.drop('Timestamp', axis=1)
survey_df.columns = ['Name','email','phone','role','Zions Harp',
                    'Gospel Hymns','Hymns of Zion','Celebration Hymnal',
                    'Junior Hymnal', 'Camp Book','Dates off','Capacity','Weekly_preference']
survey_df.set_index("Name",inplace=True)
## Changing Inputs from Yes/No and capacity to bool and 3,2,1 respecively
for column in survey_df.columns:
    survey_df[column] = survey_df[column].map(lambda x: True if x == 'Yes' else (False if x == 'No' else x))

## Creating the lists of Capacity per month
Leader_list = []
Piano_list = []

## The program multi_append(Str, num) produces a list with Str, n times.
def multi_append(name, n):
    l = []
    for i in range(0,n):
        l.append(name)
    return l

## The program below creates a list of leaders/piano names * the number of times they are able to
##   play a month

for index, row in survey_df.iterrows():
    if row["Capacity"] == "0 (reserve)":
        row["Capacity"] = 0
    row["Capacity"] = int(row["Capacity"])
    if row['role'] == 'Leader':
        Leader_list.extend(multi_append(index, row['Capacity']))
    elif row["role"] == 'Both':
        Leader_list.extend(multi_append(index, row['Capacity'] // 2))
        Piano_list.extend(multi_append(index, row['Capacity'] // 2))
    else:
        Piano_list.extend(multi_append(index, row['Capacity']))
## Inputs the dates for 4 months, starting with start_month. 
##   Change this out for the input option month.

df = pd.DataFrame({'Start Date':pd.date_range(begin_date, periods=120),
                   'End Date':pd.date_range(begin_date, periods=120)})
dates_avail = pd.DataFrame(index=df['Start Date'],columns=(survey_df.index))

## Filters out rows that are not wednesdays or Sundays
for index, row in df.iterrows():
    if row['Start Date'].weekday() == 6:
        continue
    elif row['Start Date'].weekday() == 2:
        continue
    else:
        df.drop(index, inplace=True)

## Creates Additional Sunday placement.
temp_df = []
for index, row in df.iterrows():
    if row['Start Date'].weekday() == 6:
        temp_df.extend([list(row)]*2)
    else:
        temp_df.append(list(row))

df = pd.DataFrame(temp_df, columns=df.columns)

## Implementing Sit/Stand format
def format(row):
    if row['Start Date'].weekday() == 6:
        return 'Sit'
    else:
        return    

df['format'] = df.apply(lambda row: format(row), axis=1)

if df.loc[0,'Start Date'].weekday() == 6:
    df.loc[0,'format'] = None
else:
    df.loc[1,'format'] = None

for i in range(3, len(df) - 1):
    if df.loc[i-2,'format'] != None:
        df.loc[i,'format'] = None
    elif df.loc[i-3,'format'] == 'Sit':
        df.loc[i,'format'] = 'Stand'
    else:
        continue

## Adding start and stop times
def start_time_of_day(row):
    if row['Start Date'].weekday() == 6:
        if row['format'] == None:
            return '4:40:00 PM'
        else:
            return '5:15:00 PM'
    else:
        return '7:30:00 PM'

def end_time_of_day(row):
    if row['Start Date'].weekday() == 6:
        if row['format'] == None:
            return '5:15:00 PM'
        else:
            return '5:45:00 PM'
    else:
        return '7:55:00 PM'

df['Start Time'] = df.apply(lambda row: start_time_of_day(row), axis=1)
df['End Time'] = df.apply(lambda row: end_time_of_day(row), axis=1)

book_list = ['Gospel Hymns','Celebration Hymnal','Gospel Hymns','Hymns of Zion','Gospel Hymns',
             'Junior Hymnal','Gospel Hymns','Camp Book']

wed_book_list = ["Zions Harp","Gospel Hymns"]
pos = 0
pos2 = 0
df['Subject'] = 'Zions Harp'
for index, row in df.iterrows():
    if pos >= len(book_list):
        pos = 0
    if row['Start Date'].weekday() == 6:
        if "4:40" in row['Start Time']:
            df.loc[index,'Subject'] = 'Zions Harp'
        else:
            df.loc[index,'Subject'] = book_list[pos]
            pos += 1
    else: 
        df.loc[index,'Subject'] = wed_book_list[pos2]
        pos2 += 1
    if pos2 > 1:
        pos2 = 0
    row['Start Date'] = str(row['Start Date'])[:10]
    row['End Date'] = str(row['End Date'])[:10]

## The function below takes a list and returns a random value from the list without replacing it.
def rm_from_lst(los,x):
    for i in range(len(los)):
        if (los[i] == x):
            los.remove(los[i])

## Convert(str) takes in a string and returns a list of the string
##   broken up by a ','
def Convert(s):
    if type(s) == float:
        return []
    if '-' in s:
        li = (s.replace(' ', ''))
        li = list(s.split(","))
        return li
    else:
        return []
    
## Creating the Leader and Pianist columns
df['Leader'] = ''
df['Pianist'] = ''

## The code below splits the main schedule into 4 schedules for each month
sched_1 = df[df['Start Date'].dt.strftime('%Y-%m') == '2024-05']
sched_2 = df[df['Start Date'].dt.strftime('%Y-%m') == '2024-06']
sched_3 = df[df['Start Date'].dt.strftime('%Y-%m') == '2024-07']
sched_4 = df[df['Start Date'].dt.strftime('%Y-%m') == '2024-08']

## need to replace from list if name is not chosen.
## Populates leaders

def remove_third(los):
    if len(los) > 3:
        los = los[1:]
    return los

def time_to_name(t):
    name = "Wednesday"
    if t == '5:15:00 PM':
        name = "Sunday (1st Half)"
    elif t == '5:45:00 PM':
        name = "Sunday (2nd Half)"
    return name

previous_leaders = []
previous_pianists = []

def fill_schedule(df, leader_list, pianist_list, survey_df, prayer_services, sermonettes):

    for index, row in df.iterrows():
        # Select a leader and pianist
        leader = np.random.choice(leader_list)
        pianist = np.random.choice(pianist_list)
        # Retrieve start time
        start_time = time_to_name(row['Start Time'])
        # Ensure leader and pianist meet criteria
        while not all([
            survey_df.loc[leader, row['Subject']],
            start_time in survey_df.loc[leader, 'Weekly_preference'],
            str(row['Start Date'])[:10] not in survey_df.loc[leader, 'Dates off'],
            leader not in previous_leaders,
            leader != pianist
        ]):
            leader = np.random.choice(leader_list)

        while not all([
            survey_df.loc[pianist, row['Subject']],
            start_time in survey_df.loc[pianist, 'Weekly_preference'],
            str(row['Start Date'])[:10] not in survey_df.loc[pianist, 'Dates off'],
            pianist not in previous_pianists,
            leader != pianist
        ]):
            pianist = np.random.choice(pianist_list)
        # Assign leader and pianist
        df.at[index, 'Leader'] = leader
        df.at[index, 'Pianist'] = pianist

        for los,s in [(previous_leaders,leader),(previous_pianists,pianist)]:
            los.append(s)
            if len(los) > 3:
                los.pop(0)

        # Update subject based on dates
        if str(row['Start Date'])[:10] in prayer_services:
            df.at[index, 'Subject'] = "Prayer Service"
        elif str(row['Start Date'])[:10] in sermonettes: 
            df.at[index, 'Subject'] = "Sermonette"

# Create an empty DataFrame
main_schedule = pd.DataFrame()

# Iterate through schedules and fill them
for schedule in [sched_1, sched_2, sched_3, sched_4]:
    fill_schedule(schedule, Leader_list, Piano_list, survey_df, prayer_services, sermonettes)
    main_schedule = pd.concat([main_schedule, schedule], ignore_index=True)

final_df = main_schedule.filter(['Subject','Start Date','End Date', 'Start Time','End Time'],axis=1)

## The following code writes the description column for the final df.
def write_description(row):
    string = 'Leader: {leader} | Pianist: {pianist} \n Format: {format}'.format(leader=row['Leader'],pianist=row['Pianist'],format=row['format'])
    return string

final_df['Description'] = main_schedule.apply(lambda row: write_description(row), axis=1)

final_df.to_csv('Music_Schedule.csv')

## make_pdf(df) takes the shedule dataframe and outputs a new dataframe that is the pdf version of the schedule.
def make_pdf(df):
    new_df = pd.DataFrame(np.arange(216).reshape(18,12)).astype(str)
    i = 0
    for index, row in df.iterrows():
        if row['Start Date'].weekday() == 6:
            if row['Start Time'] == '4:40:00 PM':
                new_df.iloc[i,1] = row['Leader']
                new_df.iloc[i,2] = row['Pianist']
            else:
                new_df.iloc[i,0] = str(row['Start Date'])[:10]
                new_df.iloc[i,3] = row['Leader']
                new_df.iloc[i,4] = row['Pianist']
                new_df.iloc[i,5] = row['format']
                new_df.iloc[i,6] = row['Subject']
        else:
            new_df.iloc[i,8] = str(row['Start Date'])[:10]
            new_df.iloc[i,9] = row['Leader']
            new_df.iloc[i,10] = row['Pianist']
            new_df.iloc[i,11] = row['Subject']
            i += 1
    return new_df

pdf = make_pdf(main_schedule)
pdf.to_csv('Music_schedule_pdf_version.csv')
print("Program Complete.")