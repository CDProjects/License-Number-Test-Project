import mysql.connector
import config
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from mysql.connector.errors import Error as MySQLError

# Connect to MySQL database
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="DTWP8o#GpPH#Egp",
        database="test_schema"
    )
except MySQLError as e:
    print(f"Error connecting to MySQL database: {e}")
    exit(1)

# Create cursor
mycursor = mydb.cursor()

# Get license numbers and their corresponding table names where player_status = 1
mycursor.execute("SELECT license_number, 'license_numbers_table' as table_name FROM license_numbers_table WHERE player_status = 1 UNION SELECT license_number, 'retired_license_table' as table_name FROM retired_license_table WHERE player_status = 1")
license_numbers_data = mycursor.fetchall()

# Prefix the license numbers with A or B depending on which table they come from
prefixed_license_numbers = [('A' + str(row[0]) if row[1] == 'license_numbers_table' else 'B' + str(row[0])) for row in license_numbers_data]

# Get Google Sheets credentials and connect to sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Keys/Google Sheets API.json', scope)
client = gspread.authorize(creds)
sheet = client.open('MySQL Test Table').sheet1

# Get all license numbers from the Google Sheet
sheet_license_numbers = [row[0] for row in sheet.get_all_values()][1:]

# Prefix the license numbers in the Google Sheet with A or B if they are not already prefixed
prefixed_sheet_license_numbers = []
for license_number in sheet_license_numbers:
    if license_number[0] == 'A' or license_number[0] == 'B':
        prefixed_sheet_license_numbers.append(license_number)
    else:
        prefixed_sheet_license_numbers.append('A' + license_number)

# Create sets of the license numbers from each source
license_numbers_table = set(prefixed_license_numbers)
sheet_license_numbers = set(prefixed_sheet_license_numbers)

# Find any license numbers that are not in at least one of the sources
missing_license_numbers = sheet_license_numbers - license_numbers_table

# Create the message to be sent
message = MIMEText("Missing license numbers:\n" + "\n".join(missing_license_numbers))

# Set the sender and recipient email addresses
sender = "emailcaseydent@gmail.com"
recipient = "emailcaseydent@gmail.com"

# Set the subject of the email
message['Subject'] = 'Missing License Numbers'

# Set the sender and recipient of the email
message['From'] = sender
message['To'] = recipient

# Set up SMTP server and login
with smtplib.SMTP('smtp.gmail.com', 587, timeout=120) as smtpObj:
    smtpObj.starttls()
    try:
        smtpObj.login('emailcaseydent@gmail.com', config.EMAIL_PASSWORD)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP login error: {e}")
        exit(1)

    # Send the email
    smtpObj.sendmail(sender, recipient, message.as_string())

    # Close the connection to the SMTP server
    smtpObj.quit()
