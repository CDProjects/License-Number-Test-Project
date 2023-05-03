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

# Get all license numbers and statuses from license_numbers_table where player_status = 1
mycursor.execute("SELECT license_number FROM license_numbers_table WHERE player_status = '1'")
license_numbers_table_data = mycursor.fetchall()

# Get all license numbers and statuses from retired_license_table where player_status = 1
mycursor.execute("SELECT license_number FROM retired_license_table WHERE player_status = '1'")
retired_license_table_data = mycursor.fetchall()

# Get Google Sheets credentials and connect to sheet
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Keys/Google Sheets API.json', scope)
client = gspread.authorize(creds)
sheet = client.open('MySQL Test Table').sheet1

# Get all license numbers from the Google Sheet
sheet_license_numbers = [row[0] for row in sheet.get_all_values()][1:]

# Create sets of the license numbers from each source
license_numbers_table = set(['A' + str(row[0]) for row in license_numbers_table_data])
retired_license_table = set(['B' + str(row[0]) for row in retired_license_table_data])
sheet_license_numbers = set(sheet_license_numbers)

# Find any license numbers that are not in at least one of the sources
missing_license_numbers = sheet_license_numbers - (license_numbers_table | retired_license_table)

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

