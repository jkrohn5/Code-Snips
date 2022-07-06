import arcpy, os
import requests
import zipfile
import io
import shutil
# For Http calls
import http.client, urllib, json
from datetime import date, timedelta
##Start/Stop Service for COVID_Footprint                            
# Set server full name
serverHost = "restservice"
servicePath = "folder/service"


# A function to generate a token given username, password and the adminURL.
def getToken(serverHost):
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"
    
    params = urllib.parse.urlencode({'username': 'username', 'password': 'password', 'client': 'requestip', 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters
    httpConn = http.client.HTTPSConnection(serverHost, 443)
    httpConn.request("POST", tokenURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print ("Error while fetching tokens from admin URL. Please check the URL and try again.")
        return
    else:
        data = response.read()
        httpConn.close()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):            
            return
        
        # Extract the token from it
        token = json.loads(data)        
        return token['token']           
        
# A function that checks that the input JSON object is not an error object.
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print ("Error: JSON object returns an error. " + str(obj))
        return False
    else:
        return True
    
# A function to stop or start a map service
def stopStartService(stopStart, httpConn, params, headers, servicePath):
    stopOrStartURL = "/arcgis/admin/services/" + servicePath + ".MapServer/" + stopStart
    httpConn.request("POST", stopOrStartURL, params, headers)
    
    # Read stop response
    stopStartResponse = httpConn.getresponse()
    result = servicePath + " -- "
    if (stopStartResponse.status != 200):
        httpConn.close()
        result += "error: " + stopStart
        serviceResultFile.write(result + "\n")
        print (result)
        return
    else:
        stopStartData = stopStartResponse.read()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(stopStartData):
            result += "error: " + stopStart                            
        else:
            result += stopStart + " \t"
            
        print (result)
        httpConn.close()
        return result


# Main process start here

# Get a token
token = getToken(serverHost)
if token == "":
    print ("Could not generate a token.")
    exit

# Get the root info
serverURL = "/arcgis/admin/services/"
requestURL = "https://" + serverHost + ":443/arcgis/rest/services/"

params = urllib.parse.urlencode({'token': token, 'f': 'json'})
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

# Connect to URL and post parameters    
httpConn = http.client.HTTPSConnection(serverHost, 443)

# Stop service
stopStartService("stop", httpConn, params, headers, servicePath)

os.chdir(r'directory')
arcpy.env.overwriteOutput = True
today = date.today()
yesterday = today - timedelta(days=1)
yesterday = str(yesterday).replace("-","")
year = yesterday[:4]
month = yesterday[4:6]
url1 = 'https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/Shapefile/' + year +'/'+ month + '/hms_smoke' + yesterday + '.zip'
print('Downloading shapefiles...')
r = requests.get(url1)
z = zipfile.ZipFile(io.BytesIO(r.content))
print("Done")
z.extractall(path=r'pathtodirectory')# extract to folder
output_db = r'\\shareddrive\GeoDatabase\USGS\Wildfire\WildfirePerimeters.gdb'
shp = r'localpath\hms_smoke' + yesterday+'.shp'
print("Adding date field")
for attempt in range(3):
    try:
        arcpy.management.AddField(shp,'lastupdate','TEXT',field_length = 10)
        arcpy.management.CalculateField(shp, 'lastupdate', 'datetime.datetime.now() - datetime.timedelta(days=1)')
    except:
        print ("This failed because arcpy is dumb, trying again...")
    else:
        break
else:
    print( "This failed all three attempts. Check your code.")
inputlist = [shp]
print("Converting to GDB...")
for attempt in range(3):
    try:
        arcpy.conversion.FeatureClassToFeatureClass(shp, output_db,"LiveSmoke")
    except:
        print ("This failed because arcpy is dumb, trying again...")
    else:
        break
else:
    print( "This failed all three attempts. Check your code.")

print("Done")
for attempt in range(3):
    try:
        arcpy.management.Delete(shp)
    except:
        print ("This failed because arcpy is dumb, trying again...")
    else:
        break
else:
    print( "This failed all three attempts. Check your code.")

# Start service
stopStartService("start", httpConn, params, headers, servicePath)
