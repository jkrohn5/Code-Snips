#Author: Justin
#I've only tested this for the first couple of states
import os
import requests
import json
import io
import zipfile
import arcpy
arcpy.env.overwriteOutput = True
##Change this to working directory of your choice!
os.chdir("D:\\WorkingProjects\\FEMA2024")
base_url = 'https://hazards.fema.gov/nfhlv2/output/State/'
stfips = ['01', '02', '04', '05', '06', '08', '09', '10', '11', '12', '13', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '44', '45', '46', '47', '48', '49', '50', '51', '53', '54', '55', '56', '60', '66', '69', '72', '78']

for fips in stfips:
    #make an HTTP GET request to the endpoint to get product path for download
    response = requests.get(f'https://msc.fema.gov/portal/advanceSearch?affiliate=fema&query&selstate={fips}&selcounty={fips}001&selcommunity={fips}001C&searchedCid={fips}001C&method=search')
    #Get the response content as a JSON object
    json_obj = json.loads(response.content)
    #Extract the nested variable from the JSON object
    product_id = json_obj["EFFECTIVE"]["NFHL_STATE_DATA"][0]["product_FILE_PATH"]
    print(product_id)
    url = base_url + product_id
    response = requests.get(url)
    print(response)
    if not os.path.exists('FEMA24'):
        os.makedirs('FEMA24')
    # Save the response content to a file in the data folder
    zip_file_path = f'FEMA24/{product_id}'
    with open(zip_file_path, 'wb') as f:
        f.write(response.content)
    
    # Extract the contents of the ZIP file to a subfolder with the same name as the ZIP file (minus the ".zip" extension)
    extract_path = f'FEMA24'
    with zipfile.ZipFile(zip_file_path) as zip_file:
        zip_file.extractall(extract_path)

    os.remove(zip_file_path)
    
    print(f'Extracted {zip_file_path} to {extract_path}')
print("Downloaded and extract all data")
# Set the output geodatabase path
input_folder = r"D:\WorkingProjects\FEMA2024\FEMA24"
output_gdb = r"D:\Default.gdb"

output_fc_name = "Flood_Hazard_Layers"
out_fc = os.path.join(output_gdb, output_fc_name)
# Set the feature class name to merge
fc_name = "S_Fld_Haz_Ar"
fc_list = []
# Iterate through the geodatabases in the input folder
for gdb_name in os.listdir(input_folder):
    if gdb_name.endswith(".gdb"):  # Check if the item is a geodatabase
        gdb_path = os.path.join(input_folder, gdb_name)
        arcpy.env.workspace = gdb_path
        
        # Check for feature datasets within the geodatabase
        fds_list = arcpy.ListDatasets()
        if len(fds_list) > 0:
            for fds_name in fds_list:
                fds_path = os.path.join(gdb_path, fds_name)
                arcpy.env.workspace = fds_path
                
                # Check if the feature class exists and merge if it does
                if arcpy.Exists(fc_name):
                    fc = arcpy.ListFeatureClasses(fc_name)[0]
                    fc = os.path.join(gdb_path, fds_name, fc)
                    print("adding " + fc + " to the list")
                    fc_list.append(fc)
                  
        # If no feature datasets exist, check for the feature class in the geodatabase
        else:
            if arcpy.Exists(fc_name):
                fc = arcpy.ListFeatureClasses(fc_name)[0]
                fc = os.path.join(gdb_path, fc)
                print("adding " + fc + " to the list")
                fc_list.append(fc)
            
        # Reset the workspace to the geodatabase for the next iteration
        arcpy.env.workspace = gdb_path
        
arcpy.Merge_management(fc_list, out_fc)
arcpy.management.DeleteIdentical(out_fc, ['DFIRM_ID', 'VERSION_ID', 'FLD_AR_ID', 'STUDY_TYP', 'FLD_ZONE', 'ZONE_SUBTY', 'SFHA_TF', 'STATIC_BFE', 'V_DATUM', 'DEPTH', 'LEN_UNIT', 'VELOCITY', 'VEL_UNIT', 'AR_REVERT', 'AR_SUBTRV', 'BFE_REVERT', 'DEP_REVERT', 'DUAL_ZONE', 'SOURCE_CIT', 'GFID'])
