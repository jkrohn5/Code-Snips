#import necessary python modules
import arcpy, os
#import arcpyproduction
arcpy.env.overwriteOutput = True
#setting folder path to current folder
folderPath = r"./"

#setting environmental variables

ws = arcpy.env.workspace = folderPath
arcpy.env.overwriteOutput = True

#use arcpy to list all of the aprx files
aprxList = arcpy.ListFiles("*.aprx")

#print the total number of aprx files

if len(aprxList) == 0:
    print ("There are no aprx files found in this directory.")
if len(aprxList) == 1:
    print ("There is "+str(len(aprxList))+" aprx file found in this directory.")
if len(aprxList) > 1:
    print ("There are "+str(len(aprxList))+ " aprx files found in this directory.")

#set the count of the aprx to 0
fullCount = 0
errorCount = 0

try:
    for aprx in aprxList:
        aprx = arcpy.mp.ArcGISProject(ws + aprx)
        layout = aprx.listLayouts()[0]
        
# House districts
#number of house districts for which layouts will be created
        n_hd = int(input("How many districts?:"))
#user inputs HD GEOID2
        hd_list = []
        for i in range(n_hd):
            hd_list.append(input("Enter geoid2:"))
            print ("there are "+str(len(hd_list))+" items in this list.")
        map = aprx.listMaps()[0]
        print (map.name)
        for lyr in map.listLayers():
            #update definition query to individual geoid2 then get state/name for title
            if lyr.name == 'TIGER19_GEO_USHOUSE116':
                for geoid in hd_list:
                    lyr.definitionQuery = "Geoid2 = "+ "'"+str(geoid)+"'"
                    fields = ['StName','NameLSAD']
                    with arcpy.da.SearchCursor(lyr,fields) as cursor:
                        for row in cursor:
                            state = row[0]
                            district = row[1]
                    print ("Creating Layout for " + state +' '+ district)
                    mapframe = layout.listElements("MAPFRAME_ELEMENT")[0]
                    #get extent
                    Extent = mapframe.getLayerExtent(lyr,True)
                    titleItem = layout.listElements("TEXT_ELEMENT", "title")[0]
                    titleItem.text = state + os.linesep + district
#create bounding rectangle to determine layout orientation
                    arcpy.MinimumBoundingGeometry_management(lyr,r"./bounding_temp.shp","RECTANGLE_BY_WIDTH", mbg_fields_option="MBG_FIELDS")
                    boundingbox = r"./bounding_temp.shp"
                    cursor2 = arcpy.SearchCursor(boundingbox)
                    for row in cursor2:
                        orientation=row.MBG_Orient
                    #orientation between 0 - 180, so these loops determine whether landscape or portrait
                    if orientation >45 and orientation <= 135:
                        print ("This layout is in landscape")
                        layout.pageHeight = 11
                        layout.pageWidth = 17
                        #position elements
                        for elm in layout.listElements("TEXT_ELEMENT"):
                            if elm.name == "title":
                                elm.elementPositionX = 8.495
                                elm.elementPositionY = 2.9663
                                elm.elementWidth = 4.47
                                elm.elementHeight = 0.8811
                            if elm.name == "note":
                                elm.elementPositionX = 14.5005
                                elm.elementPositionY = 2.3306
                                elm.elementWidth = 4.0323
                                elm.elementHeight = 0.4909
                        for elm in layout.listElements("GRAPHIC_ELEMENT"):
                            if elm.name == "Rectangle":
                                elm.elementPositionX = 0.1617
                                elm.elementPositionY = 0.1617
                                elm.elementWidth = 16.6766
                                elm.elementHeight = 10.6766
                        for elm in layout.listElements("MAPFRAME_ELEMENT"):
                            if elm.name == "Layers Map Frame":
                                elm.elementPositionX = 0.323
                                elm.elementPositionY = 3.2505
                                elm.elementWidth = 16.3522
                                elm.elementHeight = 7.4039
                        for elm in layout.listElements("LEGEND_ELEMENT"):
                            if elm.name == "Legend":
                                elm.elementPositionX = 0.32
                                elm.elementPositionY = 0.627
                                elm.elementWidth = 6.0238
                                elm.elementHeight = 1.9847
                        for elm in layout.listElements("MAPSURROUND_ELEMENT"):
                            if elm.name == "Alternating Scale Bar":
                                elm.elementPositionX = 0.32
                                elm.elementPositionY = 2.2442
                                elm.elementWidth = 2.6434
                                elm.elementHeight = 0.7178
                            if elm.name == "North Arrow":
                                elm.elementPositionX = 8.495
                                elm.elementPositionY = 1.1847
                                elm.elementWidth = 1.1799
                                elm.elementHeight = 1.4582
                        for elm in layout.listElements("PICTURE_ELEMENT"):
                            if elm.name == "Logo":
                                elm.elementPositionX = 12.2596
                                elm.elementPositionY = 0.3838
                                elm.elementWidth = 4.2471
                                elm.elementHeight = 1.0436
                        mapframe.camera.setExtent(Extent)
                        #export to jpeg
                        layout.exportToJPEG(r"./"+str(geoid)+".jpg", resolution=800)
                    if orientation <=45 or orientation > 135:
                        print ("This layout is in portrait")
                        layout.pageHeight = 17
                        layout.pageWidth = 11
                        for elm in layout.listElements("TEXT_ELEMENT"):
                            if elm.name == "title":
                                elm.elementPositionX = 5.565
                                elm.elementPositionY = 3.0163
                                elm.elementWidth = 4.47
                                elm.elementHeight = 0.8811
                            if elm.name == "note":
                                elm.elementPositionX = 9.06
                                elm.elementPositionY = 1.8382
                                elm.elementWidth = 3.3781
                                elm.elementHeight = 0.4113
                        for elm in layout.listElements("GRAPHIC_ELEMENT"):
                            if elm.name == "Rectangle":
                                elm.elementPositionX = 0.1617
                                elm.elementPositionY = 0.1617
                                elm.elementWidth = 10.6766
                                elm.elementHeight = 16.6766
                        for elm in layout.listElements("MAPFRAME_ELEMENT"):
                            if elm.name == "Layers Map Frame":
                                elm.elementPositionX = 0.323
                                elm.elementPositionY = 3.2505
                                elm.elementWidth = 10.3474
                                elm.elementHeight = 13.4105
                        for elm in layout.listElements("LEGEND_ELEMENT"):
                            if elm.name == "Legend":
                                elm.elementPositionX = 0.32
                                elm.elementPositionY = 0.3812
                                elm.elementWidth = 6.02
                                elm.elementHeight = 1.9834
                        for elm in layout.listElements("MAPSURROUND_ELEMENT"):
                            if elm.name == "Alternating Scale Bar":
                                elm.elementPositionX = 0.32
                                elm.elementPositionY = 2.2169
                                elm.elementWidth = 2.3518
                                elm.elementHeight = 0.7724
                            if elm.name == "North Arrow":
                                elm.elementPositionX = 9.06
                                elm.elementPositionY = 2.5757
                                elm.elementWidth = 0.9627
                                elm.elementHeight = 1.1896
                        for elm in layout.listElements("PICTURE_ELEMENT"):
                            if elm.name == "Logo":
                                elm.elementPositionX = 7.48
                                elm.elementPositionY = 0.2397
                                elm.elementWidth = 3.16
                                elm.elementHeight = 0.7746
                        mapframe.camera.setExtent(Extent)
                        #export to jpeg
                        layout.exportToJPEG(r"./"+str(geoid)+".jpg", resolution=800)
                        print ("export complete for " + state + ' ' + district)
        arcpy.management.Delete(boundingbox)
        aprx.save()
        print ("Save complete.")
        del aprx
except Exception as e:
    print ("The following error has occured:")
    print (e.message)
    print ("Because there was an error, you should try re-running the script.")
    errorCount += 1
