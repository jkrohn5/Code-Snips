import arcpy, os
# For Http calls
import http.client as httplib, urllib, json, urllib.request as urllib2

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
    httpConn = httplib.HTTPSConnection(serverHost, 443)
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
httpConn = httplib.HTTPSConnection(serverHost, 443)

# Stop service
stopStartService("stop", httpConn, params, headers, servicePath)

arcpy.env.overwriteOutput = True
output_db = r'\\shareddrive\GeoDatabase\COVID\COVID.gdb'

# input and output feature classes
in_features_list = ["schema.listoffeatures"] 


out_features_list = [ "listoffeatureclassnames"]

# this creates a sde connection file in the default "Database Connections" folder: <computer_name>\Users\<user_name>\AppData\Roaming\ESRI\Desktop<release#>\ArcCatalog 
# you could also specify a different path to store the connection file
sde_connection = arcpy.management.CreateDatabaseConnection('pathtostoreconnection\sql-to-gdb-v3',
                                                            "cliff.sde",                                                
                                                            "SQL_SERVER",                                                            
                                                            "Instance", 
                                                            "DATABASE_AUTH",
                                                            "USERNAME",
                                                            "PASSWORD", 
                                                            "SAVE_USERNAME",
                                                            "Database",
                                                           "Schema")

arcpy.env.workspace = str(sde_connection)
arcpy.env.overwriteOutput = True

# convert feature classes from SQL to gdb
feature_class_range = range(len(in_features_list))
for i in feature_class_range:
    in_feature = in_features_list[i]
    out_feature = out_features_list[i]
    arcpy.conversion.FeatureClassToFeatureClass(in_feature, output_db, out_feature)
#add index if needed
arcpy.management.AddIndex(r'\\pathtogdb.gdb\featureclass',["timefield"],"timseries","NON_UNIQUE","ASCENDING")    
# Start service
stopStartService("start", httpConn, params, headers, servicePath)
