import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

api_key = "" ## Google API key is required
## If you have a Google Places API key, enter it here
## api_key = 'AIzaSy___IDByT70'


if api_key is False:
	serviceurl = "http://py4e-data.dr-chuck.net/geojson?"
else:
	serviceurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

## Additional detail for urllib
## http.client.HTTPConnection.debuglevel = 1

connectionFile = sqlite3.connect("databasesAndVisualization.sqlite")
cursorHandle = connectionFile.cursor()

cursorHandle.execute('''CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

## Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

fileHandle = open("where.data")
count = 0
for line in fileHandle:
	##print(line)
	if count > 200:
		print("Retrieved 200 locations, restart to retrieve more!")
		break
	address = line.strip()
	print("")
	cursorHandle.execute('''SELECT geodata FROM Locations WHERE address = ?''',(memoryview(address.encode()),))

	try:
		data = cursorHandle.fetchone()[0]
		print("Found in database",address)
		continue
	except:
		pass

	parms = dict()
	parms["query"] = address
	if api_key is not False:
		parms["key"] = api_key

	url = serviceurl + urllib.parse.urlencode(parms)

	print("Retrieving",url)
	urlHandle = urllib.request.urlopen(url,context=ctx)
	data = urlHandle.read().decode()
	print("Retrieved",len(data),"characters",data[:20].replace("\n"," "))
	count = count + 1

	try:
		js = json.loads(data)
	except:
		print(data) ## We print in case unicode causes an error
		continue

	if "status" not in js or (js["status"] != "OK" and js["status"] != "ZERO_RESULTS"):
		print("================= Failure to retrieve =================")
		print(data)
		break

	cursorHandle.execute('''INSERT INTO Locations (address, geodata)
		VALUES (?,?)''',(memoryview(address.encode()),memoryview(data.encode())))

	connectionFile.commit()

	if count % 10 == 0:
		print("Pausing fo a bit...")
		time.sleep(3)

print("Run geodump.py to read the data from the database so you can vizualize it on a map.")
