# Music Scheduling Program

The Music Scheduling Program is a tool designed to automate the creation of music schedules for events. It allows users to input participant data, preferences, and availability, and outputs a CSV file that can be imported into a calendar application. The program also supports integration with Google Calendar for automatic event creation.

---

## Features

- **Automated Scheduling**: Generates schedules based on participant roles, availability, and preferences.
- **Flexible Input**: Supports input via Google Forms (Google Sheets) or a manually provided TSV file.
- **Calendar Integration**: Optionally uploads the schedule to Google Calendar.
- **CSV Output**: Produces a CSV file that can be imported into calendar applications.

---

## Requirements

### Python Version
- Python 3.8 or higher

### Required Libraries
Install the required libraries using `pip`:
```bash
pip install pandas numpy scikit-learn google-api-python-client
```

---

## Setup

### Option 1: Using Google Cloud
1. **Enable APIs**:
   - Enable the Google Sheets and Google Calendar APIs in your Google Cloud project.
2. **Service Account**:
   - Create a service account in your Google Cloud project.
   - Download the service account JSON file and place it in the project directory.
   - Update the `SERVICE_ACCOUNT_FILE` path in `Scheduling.py` to point to the JSON file.
3. **Set Constants**:
   - Update the `SPREADSHEET_ID` and `CALENDAR_ID` constants in `Scheduling.py` with your Google Sheets and Calendar IDs.

### Option 2: Using a TSV File
1. **Prepare the Input File**:
   - Create a TSV file with the following columns:
     - `Name`: Name of the participant.
     - `Role`: Role of the participant (`Leader`, `Pianist`, or `Both`).
     - `Dates off`: Dates the participant is unavailable.
     - `Weekly preference`: Preferred days/times for participation.
     - `Capacity`: Number of times the participant can serve per month.
     - `Subject`: Preferred subjects (e.g., `Zions Harp`, `Gospel Hymns`).
2. **Place the File**:
   - Save the TSV file in the project directory or provide its path when running the program.

---

## Usage

### Command Line
Run the program from the command line:
```bash
python Scheduling.py input_schedule.tsv output_schedule.csv
```
- Replace `input_schedule.tsv` with the path to your TSV file.
- Replace `output_schedule.csv` with the desired output file path.

### Graphical Interface
1. Run the GUI program:
   ```bash
   python gui.py
   ```
2. Use the GUI to:
   - Select the input TSV file.
   - Specify the output CSV file.
   - Generate the schedule.

---

## Output

The program generates a CSV file with the following columns:
- `Subject`: The subject of the event.
- `Start Date`: The start date of the event.
- `Start Time`: The start time of the event.
- `End Time`: The end time of the event.
- `Leader`: The assigned leader.
- `Pianist`: The assigned pianist.

### Importing to a Calendar
1. Open your calendar application (e.g., Google Calendar).
2. Use the "Import" feature to upload the generated CSV file.

---

## Example Input and Output

### Example Input (TSV)
```plaintext
Name    Role    Dates off   Weekly preference    Capacity    Subject
John    Leader  2024-05-10  Sunday PM            3           Zions Harp
Jane    Pianist 2024-05-15  Wednesday PM         2           Gospel Hymns
```

### Example Output (CSV)
```csv
Subject,Start Date,Start Time,End Time,Leader,Pianist
Zions Harp,2024-05-01,5:15:00 PM,5:45:00 PM,John,Jane
Gospel Hymns,2024-05-03,7:30:00 PM,7:55:00 PM,John,Jane
```

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to submit a pull request or open an issue.

---

## Contact

For questions or support, please contact the project maintainer.