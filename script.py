import mysql.connector
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Connect to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="DTWP8o#GpPH#Egp",
  database="test_schema"
)

# Create cursor
mycursor = mydb.cursor()

# Get all license numbers and statuses from license_numbers_table where player_status = 1
mycursor.execute("SELECT license_number FROM license_numbers_table WHERE player_status = '1'")
table1_data = mycursor.fetchall()

# Get all license numbers and statuses from retired_license_table where player_status = 1
mycursor.execute("SELECT license_number FROM retired_license_table WHERE player_status = '1'")
table2_data = mycursor.fetchall()

# Get Google Sheets credentials and connect to sheet
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('YOUR_CREDENTIALS_FILE.json', scope)
client = gspread.authorize(creds)
sheet = client.open('MySQL Test').sheet1

# Get all license numbers from the Google Sheet
sheet_license_numbers = [row[0] for row in sheet.get_all_values()][1:]

# Create sets of the license numbers from each source
table1_license_numbers = set(['A' + str(row[0]) for row in table1_data])
table2_license_numbers = set(['B' + str(row[0]) for row in table2_data])
sheet_license_numbers = set(sheet_license_numbers)

# Find any license numbers that are not in at least one of the sources
missing_license_numbers = sheet_license_numbers - (table1_license_numbers | table2_license_numbers)

# Print out the missing license numbers
print("Missing license numbers:")
for license_number in missing_license_numbers:
    print(license_number)
