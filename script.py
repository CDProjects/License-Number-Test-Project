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

# Compile all license numbers into a single list
all_license_numbers = prefixed_license_numbers_license_table + prefixed_license_numbers_retired_table

# Get Google Sheets credentials and connect to the sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file('Keys/Google Sheets API.json', scopes=scope)
client = gspread.authorize(credentials)
sheet = client.open('MySQL Test Table').sheet1

# Get all license numbers from the Google Sheet
sheet_license_numbers = [row[0] for row in sheet.get_all_values()][1:]

# Compare the license numbers from MySQL with the ones in the Google Sheet
missing_license_numbers = [license_number for license_number in sheet_license_numbers if license_number not in all_license_numbers]

# Find license numbers in all_license_numbers that are not in the Google Sheet
additional_missing_license_numbers = [license_number for license_number in all_license_numbers if license_number not in sheet_license_numbers]

# Combine the missing license numbers from both sources
all_missing_license_numbers = missing_license_numbers + additional_missing_license_numbers

# Create the message to be sent
message = MIMEText("Missing license numbers:\n" + "\n".join(all_missing_license_numbers))

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
    if all_missing_license_numbers:
        # Send the email
        smtpObj.sendmail(sender, recipient, message.as_string())

    # Close the connection to the SMTP server
    smtpObj.quit()
