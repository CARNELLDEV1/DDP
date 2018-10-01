#-----------------------------------------------------------------------------
# Name:        Cuttingline Helper Toolbox.py 
#
# Purpose:     This code is used for create cutting lines based on indexlayer
#
# Author:      Hao Ye   
#
# Created:     21/05/2018
# Copyright:   (c)Hao Ye 2018
# Licence:     <your licence>
#-----------------------------------------------------------------------------

import arcpy
import json
import os
import pythonaddins
from string import ascii_uppercase

def main():
    pass

if __name__== '__main__':
    main()
       
# Configure current layer file as main working file
mxd = arcpy.mapping.MapDocument("CURRENT") 
mxdLocation = os.path.dirname(mxd.filePath)

'''CONFIGURATION CODE BLOCK'''
# GUI Interface
ddpLoad = arcpy.GetParameterAsText(0) 
indexLay = arcpy.GetParameterAsText(1)              # Strip produced index layer
cutLineLay = arcpy.GetParameterAsText(2)            # Cutting output directors
smbolLyr = arcpy.GetParameterAsText(3)              # Cutting output directory

# Data Frames
dfMaster = arcpy.mapping.ListDataFrames(mxd)[0]     # Data frame Setting
dfChild = arcpy.mapping.ListDataFrames(mxd)[1]

if ddpLoad == "No":
    arcpy.AddMessage("\nReminder: please enable the DDP and load site drawing template. \n")
    quit()

arcpy.AddMessage("\nData processing starts, please wait. \n")

# Pre-clearning Cuttling Line
for df in arcpy.mapping.ListDataFrames(mxd):
    for layer in df:
        if layer.name == "Cuttingline":
            arcpy.mapping.RemoveLayer(df,layer)

# Cutting Lines
geometryType = "POLYLINE"
outfileName= "Cuttingline.shp"
outfilePath = os.path.join(cutLineLay + '\\')
spatailRef = arcpy.Describe(indexLay).spatialReference          

'''CUTTING LINE IMPLEMENTATION CODE BLOCK'''

# Check if indexlayer is a Polygon layer 
shapeType = arcpy.Describe(indexLay).shapeType
if shapeType != "Polygon":
   arcpy.AddMessage("\nYour input indexlayer is not Polygon Type!. \n")
   quit()

# Check if cuttingline shpfile exist
if os.path.exists(outfilePath + outfileName):
    arcpy.Delete_management(outfilePath + outfileName)
    arcpy.CreateFeatureclass_management(outfilePath, outfileName, geometryType, indexLay, "DISABLED", "DISABLED", spatailRef) 
else:
    arcpy.CreateFeatureclass_management(outfilePath, outfileName, geometryType, indexLay, "DISABLED", "DISABLED", spatailRef)    

#----Test
rows = arcpy.SearchCursor(indexLay,["PageNumber","Shape"])
rowcount = arcpy.GetCount_management(indexLay)
rowNum = int(rowcount[0])
PolyFeatures = []
PageList = []

# To loop and capture the coordinates from vertices of each polygon
arcpy.AddMessage("\nCapturing cuttline vertices... \n")
for row in rows:
    jsonString = row.Shape.JSON             # vertices can be read in JSON, WTK formats only
    dictVic = json.loads(jsonString)        # Convert a Json string to a dictionary
    verticesList = dictVic['rings']         # Key 'ring' store all coordinates in list

    for vertice in verticesList:            # by default, polygons are rectangle with 4 vertices
            vertice_1 = vertice[0]
            vertice_2 = vertice[1]
            vertice_3 = vertice[2]
            vertice_4 = vertice[3]
    
    # Recreate four points to product polylines 
    Point_1 = arcpy.Point(vertice_1[0],vertice_1[1])
    Point_2 = arcpy.Point(vertice_2[0],vertice_2[1])
    Point_3 = arcpy.Point(vertice_3[0],vertice_3[1])
    Point_4 = arcpy.Point(vertice_4[0],vertice_4[1])

    # Create left and right polyline based on the points
    PolyL = arcpy.Polyline(arcpy.Array([Point_1,Point_2]), spatailRef)
    #PolyR = arcpy.Polyline(arcpy.Array([Point_3,Point_4]), spatailRef)     # if the other line is required

    # Append polylines in the the Polyline array
    PolyFeatures.append(PolyL)
    #PolyFeatures.append(PolyR)                                             # if the other line is required

    # Append page to pagelist
    value = int(row.getValue('PageNumber'))
    PageList.append(value)

    #PageList.append(long(row.getValue('PageNumber')))                      # if the other line is required

del rows

# To loop and insert polyline geometries into the new shapefile
shapeCursor = arcpy.da.InsertCursor(outfilePath + outfileName, ['SHAPE@'])
arcpy.AddMessage("\nInserting cuttline features... \n")
for feature in PolyFeatures:
    shapeCursor.insertRow([feature])

del shapeCursor

# Configure the field table for cuttingline layer

delFields = ["OID_","GroupId","SeqId","Next","LeftPage","Previous","RightPage","TopPage","BottomPage","Angle","Shape_Leng","Shape_Area"]
arcpy.DeleteField_management(outfilePath + outfileName, delFields)
arcpy.AddField_management(outfilePath + outfileName, "Cutline_ID", "string", field_is_nullable="NULLABLE")

updateaField  = ["FID","PageNumber","Cutline_ID"]
cutLabel = "CUTTLINE "
arcpy.AddMessage("\nUpdating cuttline attributes... \n")
rowCursor =  arcpy.da.UpdateCursor(outfilePath + outfileName, updateaField)
for row in rowCursor:
    for i in range(0,100):
            if row[0] == i:
                row[1] = PageList[i]  
                row[2] = cutLabel + "A" + str(i)
                rowCursor.updateRow(row)

del rowCursor

'''DDP PRODUCTION CODE BLOCK'''

# Retrieve DDP in according to current data frame
dataDrivenPage = mxd.dataDrivenPages  

# Create Cuttline to dataframe
tempLayer = arcpy.mapping.Layer(outfilePath + outfileName)
arcpy.ApplySymbologyFromLayer_management(tempLayer, smbolLyr)

if tempLayer.supports("LABELCLASSES"):
    tempLayer.showLabels

# Add the cutting lines to the dataframe
arcpy.AddMessage("\nAdding cuttline to dateframe... \n")
arcpy.mapping.AddLayer(dfMaster, tempLayer,"TOP")
arcpy.mapping.AddLayer(dfChild, tempLayer,"TOP")

arcpy.RefreshActiveView()
arcpy.RefreshTOC()
