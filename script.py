import mysql.connector
import config
import gspread
from google.oauth2 import service_account
from email.mime.text import MIMEText
import smtplib

# Connect to MySQL database
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="DTWP8o#GpPH#Egp",
        database="test_schema"
    )
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL database: {e}")
    exit(1)

# Create cursor
mycursor = mydb.cursor()

# Get license numbers with player_status = 1 from license_numbers_table
mycursor.execute("SELECT license_number FROM license_numbers_table WHERE player_status = 1")
license_numbers_license_table = mycursor.fetchall()

# Prefix the license numbers with 'A'
prefixed_license_numbers_license_table = ['A' + str(row[0]) for row in license_numbers_license_table]

# Get license numbers with player_status = 1 from retired_license_table
mycursor.execute("SELECT license_number FROM retired_license_table WHERE player_status = 1")
license_numbers_retired_table = mycursor.fetchall()

# Prefix the license numbers with 'B'
prefixed_license_numbers_retired_table = ['B' + str(row[0]) for row in license_numbers_retired_table]

# Get Google Sheets credentials and connect to sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file('Keys/Google Sheets API.json', scopes=scope)
client = gspread.authorize(credentials)
sheet = client.open('MySQL Test Table').sheet1

# Get all license numbers from the Google Sheet
sheet_license_numbers = [row[0] for row in sheet.get_all_values()][1:]

# Create sets of the license numbers from each source
license_numbers_license_table = set(prefixed_license_numbers_license_table)
license_numbers_retired_table = set(prefixed_license_numbers_retired_table)
sheet_license_numbers = set(sheet_license_numbers)

# Find missing license numbers in the license_numbers_license_table
missing_license_numbers_license_table = sheet_license_numbers - license_numbers_license_table

# Find missing license numbers in the retired_license_table
missing_license_numbers_retired_table = sheet_license_numbers - license_numbers_retired_table

# Find missing license numbers in the Google Sheet but present in the compiled list
missing_license_numbers_in_sheet = license_numbers_license_table.union(license_numbers_retired_table) - sheet_license_numbers

# Combine all missing license numbers
missing_license_numbers = missing_license_numbers_license_table.union(missing_license_numbers_retired_table, missing_license_numbers_in_sheet)

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

    # Send the email if there are missing license numbers
    if missing_license_numbers:
        # Send the email
        smtpObj.sendmail(sender, recipient, message.as_string())

# Close the connection to the SMTP server
smtpObj.quit()
