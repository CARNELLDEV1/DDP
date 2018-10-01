#-----------------------------------------------------------------------------
# Name:        DataFrameProcessor.py
#
# Purpose:     This code is used for exporting clean the data from data frame or
#              clean and copy all the layers from the other dataframe
#
# Author:      Hao Ye
#
# Created:     16/05/2018
# Copyright:   (c)Hao Ye 2018
# Licence:     <your licence>
#-----------------------------------------------------------------------------

import arcpy
import os
import pythonaddins

def main():
    pass

if __name__== '__main__':
    main()

# Configure current layer file as main working file
mxd = arcpy.mapping.MapDocument("CURRENT")
mxdLocation = os.path.dirname(mxd.filePath)

# Data Frames Input
masterDfName = arcpy.GetParameterAsText(0)            # Master Data Frame
targetDfName = arcpy.GetParameterAsText(1)            # Target Data Frame
dfOption = arcpy.GetParameterAsText(2)                # Option List

# Give all dataframe in the mxd
for df in arcpy.mapping.ListDataFrames(mxd):
    if df.name == masterDfName:
        masterDf = df
    if df.name == targetDfName:
        TartgetDf = df
    
if dfOption == "Prepare All":
    arcpy.AddMessage("\nData processing starts, please wait. \n")

    # Clean cuttingline shapelayer in fild folder
    cutlineInFolder = "M:\ArcGIS Development\Site Drawing Automation\Index Data\Cuttingline.shp"
    if os.path.exists(cutlineInFolder):
        arcpy.Delete_management(cutlineInFolder)

    # Clean cuttingline shapelayer in dataframe
    for df in arcpy.mapping.ListDataFrames(mxd):
        for layer in df:
            if layer.name == "Cuttingline":
                arcpy.mapping.RemoveLayer(df,layer)
    
    arcpy.AddMessage("\nAll cuttingline is removed. \n")

    # Clean all the shapelayers in data frame
    for df in arcpy.mapping.ListDataFrames(mxd):
        if df.name == targetDfName:
            for layer in df:
                arcpy.mapping.RemoveLayer(df,layer)
    arcpy.AddMessage("\nAll layers in Dataframe: " + targetDfName + " are removed. \n")
    
    polyline_location = "M:\ArcGIS Development\Site Drawing Automation\Index Data\DDP.gdb\POLYLINE_DDP"
    polygon_location = "M:\ArcGIS Development\Site Drawing Automation\Index Data\DDP.gdb\POLYGON_DDP"

    # Clean all features in the dataframe
    arcpy.DeleteFeatures_management(polyline_location)
    arcpy.DeleteFeatures_management(polygon_location)
    arcpy.AddMessage("\nAll features in Polyline and Polygon are deleted, ready to use. \n")

    # Operation is selected as Prepare All
    numLayer = len(arcpy.mapping.ListLayers(mxd,"",TartgetDf))

    # Copy all contents
    if numLayer == 0:
        masterDf = arcpy.mapping.ListDataFrames(mxd)[0]
        for layer in masterDf:
            arcpy.mapping.AddLayer(TartgetDf,layer,"BOTTOM")
            
    arcpy.AddMessage("\nAll layers are successfully copied\n")

# Operation is selected as Remove Only - remove all the layers from the dataframe
if dfOption == "Remove Layers":
    arcpy.AddMessage("\nData processing starts, please wait. \n")
    for df in arcpy.mapping.ListDataFrames(mxd):
        if df.name == targetDfName:
            for layer in df:
                arcpy.mapping.RemoveLayer(df,layer)
    arcpy.AddMessage("\nAll layers in dataframe are removed.\n")  

# Operation is selected as Remove and Copy - Clean dataframe and copy all the layers
if dfOption == "Copy Layers":
    arcpy.AddMessage("\nData processing starts, please wait. \n")
    # Clean first
    numLayer = len(arcpy.mapping.ListLayers(mxd,"",TartgetDf))
    
    if numLayer!= 0:
       for layer in TartgetDf:
           arcpy.mapping.RemoveLayer(TartgetDf,layer)
       for layer in masterDf:
           arcpy.mapping.AddLayer(TartgetDf,layer,"BOTTOM")
           
    # Copy Layers
    if numLayer == 0:
        masterDf = arcpy.mapping.ListDataFrames(mxd)[0]
        for layer in masterDf:
            arcpy.mapping.AddLayer(TartgetDf,layer,"BOTTOM")
            
    arcpy.AddMessage("\nAll layers are Copied. \n")

# Operation is selected as Clean Geodatabase   
if dfOption == "Clean Geodatabase":
    arcpy.AddMessage("\nData processing start, please wait. \n")
    
    polyline_location = "M:\ArcGIS Development\Site Drawing Automation\Index Data\DDP.gdb\POLYLINE_DDP"
    polygon_location = "M:\ArcGIS Development\Site Drawing Automation\Index Data\DDP.gdb\POLYGON_DDP"

    # Clean all features in the dataframe
    arcpy.DeleteFeatures_management(polyline_location)
    arcpy.DeleteFeatures_management(polygon_location)
    arcpy.AddMessage("\nAll features in Polyline and Polygon are deleted, ready to use. \n")

# Refresh the dataframe
arcpy.RefreshActiveView()
    


