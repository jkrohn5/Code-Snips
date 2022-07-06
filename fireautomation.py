import arcpy, os
import requests
import zipfile
import io
import shutil
# For Http calls
import http.client, urllib, json

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

os.chdir(r'directorypath')
arcpy.env.overwriteOutput = True
url1 = 'https://opendata.arcgis.com/api/v3/datasets/9838f79fb30941d2adde6710e9d6b0df_0/downloads/data?format=shp&spatialRefId=4326'
print('Downloading shapefile...')
r = requests.get(url1)
z = zipfile.ZipFile(io.BytesIO(r.content))
print("Done")
z.extractall(path=r'directorypath')# extract to folder
output_db = r'\\shareddrive\GeoDatabase\USGS\Wildfire\WildfirePerimeters.gdb'
shp1 = r'C:\directorypath\FH_Incident.shp'
print("Converting to GDB...")
arcpy.conversion.FeatureClassToFeatureClass(shp1, output_db,"LiveFire")
print("Done")
arcpy.management.Delete(shp1)
# Start service
stopStartService("start", httpConn, params, headers, servicePath)
