#-----------------------------------------------------------------------------
# Name:        Module DDP Batch Production Toolbox.py
#
# Purpose:     This code is used for exporting site drawings in batch using
#              data driven page technique
#
# Author:      Hao Ye
#
# Created:     16/05/2018
# Copyright:   (c)Hao Ye 2018
# Licence:     <your licence>
#-----------------------------------------------------------------------------

import arcpy
import json
import os
import pythonaddins
import shutil

def main():
    pass

if __name__== '__main__':
    main()

# Configure current layer file as main working file

mxd = arcpy.mapping.MapDocument("CURRENT")
mxdLocation = os.path.dirname(mxd.filePath)

# Clean all PDF files before data processing to avoid conflicts
drawingLoc = "M:\ArcGIS Development\Site Drawing Automation\Index Data\Site Drawings PDF"+"\\"
filelist = [ f for f in os.listdir(drawingLoc) if f.endswith(".pdf") ]
for f in filelist:
    os.remove(os.path.join(drawingLoc, f))
arcpy.AddMessage("\nFile export directory is cleaned\n")

'''CONFIGURATION CODE BLOCK'''

# GUI Interface
indexLay = arcpy.GetParameterAsText(0)              # Strip produced index layer
outputType = arcpy.GetParameterAsText(1)            # DDP output type - PDF or MXD
outputDict = arcpy.GetParameterAsText(2)            # DDP output directory
ddpScale = arcpy.GetParameterAsText(3)              # Data Frame Scale -default: 500
scheArea = arcpy.GetParameterAsText(4)              # Scheme area
scheName = arcpy.GetParameterAsText(5)              # Scheme name
scheNumb = arcpy.GetParameterAsText(6)              # Scheme number
drawinby = arcpy.GetParameterAsText(7)              # Drawing by list
curtDate = arcpy.GetParameterAsText(8)              # Scheme date
revision = arcpy.GetParameterAsText(9)              # Revision
mapping = arcpy.GetParameterAsText(10)             # Mapping Option

# Data Frames
dfMaster = arcpy.mapping.ListDataFrames(mxd)[0]     # Data frame Setting
dfChild = arcpy.mapping.ListDataFrames(mxd)[1]      # Data frame Setting
dfMaster.scale = ddpScale                           # Data frame Scale
dfChild .scale = ddpScale                           # Data frame Scale

# Copy Data Frame and check data type
dfCopy = arcpy.mapping.ListDataFrames(mxd)[0]
shapeType = arcpy.Describe(indexLay).shapeType
if shapeType != "Polygon":
   #pythonaddins.MessageBox("Your input indexlayer is not Polygon Type!", 'Warning', 0)
   arcpy.AddError("\nYour input indexlayer is not Polygon Type!\n")
   quit()

# Retrieve DDP in according to current data frame
dataDrivenPage = mxd.dataDrivenPages
# Search cursor to read rows from indexlayer and count row number
rows = arcpy.SearchCursor(indexLay,["PageNumber","Shape"])
rowcount = arcpy.GetCount_management(indexLay)
rowNum = int(rowcount[0])
PolyFeatures = []
PageList = []

#pythonaddins.MessageBox("There is a total of" + " " + str(rowNum) + " " + "DDP Pages that can be exported", 'Confirmation', 0)
arcpy.AddMessage("\nThere is a total of" + " " + str(rowNum) + " " + "DDP Pages that can be exported. \n")

'''POPULATE MAP ELEMENT'''
elems = arcpy.mapping.ListLayoutElements(mxd)
for e in elems:
    if e.name == "Area_Text":
        e.text = scheArea
    if e.name == "Drawn_By":
        e.text = drawinby
    if e.name == "Schem_Name":
        e.text = scheName
    if e.name == "Sche_Num":
        e.text = scheNumb
    if e.name == "Scale_Text":
        e.text = ddpScale
    if e.name == "Curt_Date":
        e.text = curtDate
    if e.name == "Revision":
        e.text = revision

#pythonaddins.MessageBox("Map elements have been populated",'Report', 0)
arcpy.AddMessage("\nMap elements have been populated. \n")

'''OUTPUT CLIPPING MAPPING FILES'''

mappingFeature = mapping
mappingFileFolder = outputDict + "\\" + "Mapping"
mappingFilePath = mappingFileFolder + "\\"

if not os.path.exists(mappingFileFolder):
    os.makedirs(mappingFileFolder)
    arcpy.GraphicBuffer_analysis("POLYLINE_DDP", mappingFilePath + "MappingBuffered", "800 Feet", "SQUARE", "MITER")
    arcpy.Clip_analysis(mappingFeature, mappingFilePath + "MappingBuffered.shp",mappingFilePath + scheName + ".shp" )
    arcpy.Delete_management(mappingFilePath + "MappingBuffered.shp")
    arcpy.AddMessage("\nMappings are exported. \n")
else:
    fileList = os.listdir(mappingFileFolder)
    for fileName in fileList:
        os.remove(mappingFileFolder+"/"+fileName)
    arcpy.GraphicBuffer_analysis("POLYLINE_DDP", mappingFilePath + "MappingBuffered", "800 Feet", "SQUARE", "MITER")
    arcpy.Clip_analysis(mappingFeature, mappingFilePath + "MappingBuffered.shp",mappingFilePath + scheName + ".shp" )
    arcpy.Delete_management(mappingFilePath + "MappingBuffered.shp")
    arcpy.AddMessage("\nMappings are exported. \n")

'''OUTPUT CUTTLINE BLOCK'''

# Output all cuttlines under a sub directory
cutlineFeature = "Cuttingline"
cutlineLocation = outputDict + "\\" + "Cuttline Folder"

if not os.path.exists(cutlineLocation):
    os.makedirs(cutlineLocation)
    arcpy.FeatureClassToShapefile_conversion(cutlineFeature, cutlineLocation)
    arcpy.AddMessage("\nCuttline is exported. \n")
else:
    fileList = os.listdir(cutlineLocation)
    for fileName in fileList:
        os.remove(cutlineLocation+"/"+fileName)
    arcpy.FeatureClassToShapefile_conversion(cutlineFeature, cutlineLocation)
    arcpy.AddMessage("\nCuttline is exported. \n")

'''DDP PRODUCTION CODE BLOCK'''

# Create a new folder to save site drawings under the same directory of MXD

mxdLocation = os.path.dirname(mxd.filePath)
drawingFolder = mxdLocation + "\\" + "Site Drawings"
if not os.path.exists(drawingFolder):
    os.makedirs(drawingFolder)
else:
    fileList = os.listdir(drawingFolder)
    for fileName in fileList:
        os.remove(drawingFolder + "/" + fileName)

# Loop the rows to get polygon extent and apply them to the dataframes
siteDrawingString = scheName+ "_Site_Drawing_ "
rows = arcpy.SearchCursor(indexLay,["PageNumber","Shape"])

arcpy.AddMessage("\nDDP pages are processing,please wait.\n")

if rowNum % 2 == 0: # Even number pages
    for row in rows:
        pageNum = int(row.getValue("PageNumber"))   # Odd page
        if pageNum % 2 != 0:
            MasterExtent = row.getValue("Shape").extent
            dfChild.rotation = row.getValue("Angle")
            dfChild.panToExtent(MasterExtent)
            prtOPage = str(pageNum)
            #page = str(pageNum%2 + 1)
        else:
            ChildExtent = row.getValue("Shape").extent
            dfMaster.rotation = row.getValue("Angle")
            dfMaster.panToExtent(ChildExtent)
            prtEvenPage = str(pageNum)
            page = str(pageNum/2)

            # Update data map element
            elems = arcpy.mapping.ListLayoutElements(mxd)
            for e in elems:
                if e.name == "Draw_Num":
                    e.text = "SD_00" + str(pageNum/2)
                if e.name == "SheetS":
                    e.text = str(pageNum/2)
                if e.name == "SheetE":
                    e.text = str(rowNum/2)

            if os.path.exists(drawingFolder + siteDrawingString + page + ".pdf"):
                arcpy.Delete_management(drawingFolder + "\\" + siteDrawingString + page + ".pdf")
            else:
                arcpy.mapping.ExportToPDF(mxd, drawingFolder + "\\" + siteDrawingString + page + ".pdf")

    del rows

if rowNum % 2 != 0:
    for row in rows:
        pageNum = int(row.getValue("PageNumber"))
        if pageNum % 2 != 0 and pageNum != rowNum:                         # Odd number
            MasterExtent = row.getValue("Shape").extent
            dfChild.rotation = row.getValue("Angle")
            dfChild.panToExtent(MasterExtent)
            prtOddPage = pageNum
            #page = str(pageNum%2 + 1)

        if pageNum % 2 == 0:
            ChildExtent = row.getValue("Shape").extent
            dfMaster.rotation = row.getValue("Angle")
            dfMaster.panToExtent(ChildExtent)
            prtEvenPage = str(pageNum)
            page = str(pageNum/2)
            #page = str(pageNum%2 + 1)

            # Update data map element
            elems = arcpy.mapping.ListLayoutElements(mxd)
            for e in elems:
                if e.name == "Draw_Num":
                    e.text = "SD_00" + str(pageNum/2)
                if e.name == "SheetE":
                    e.text = str(rowNum/2 + 1)
                if e.name == "SheetS":
                    e.text = str(pageNum/2)

            if os.path.exists(drawingFolder + "\\" + siteDrawingString + page + ".pdf"):
                arcpy.Delete_management(drawingFolder + "\\" + page + ".pdf")
            else:
                arcpy.mapping.ExportToPDF(mxd, drawingFolder + "\\" + siteDrawingString + page + ".pdf")

        if pageNum == rowNum: # Last page
            MasterExtent = row.getValue("Shape").extent
            dfMaster.rotation = row.getValue("Angle")
            dfChild.rotation = row.getValue("Angle")
            dfMaster.panToExtent(MasterExtent)
            dfChild.panToExtent(ChildExtent)
            page = str(pageNum/2+1)
            
            # Update data map element
            elems = arcpy.mapping.ListLayoutElements(mxd)
            for e in elems:
                if e.name == "Draw_Num":
                    e.text = "SD_00" + str((rowNum/2)+1)
                if e.name == "SheetS":
                    e.text = str((rowNum/2) + 1)
                if e.name == "SheetE":
                    e.text = str((rowNum + 1)/2)

            if os.path.exists(drawingFolder + "\\" + siteDrawingString + page + ".pdf"):
                arcpy.Delete_management(drawingFolder + "\\" + siteDrawingString + page + ".pdf")
            else:
                arcpy.mapping.ExportToPDF(mxd, drawingFolder + "\\" + siteDrawingString + page + ".pdf")
                
            arcpy.RefreshActiveView()
    del rows

del mxd

arcpy.AddMessage('\nThe site drawings' + scheName + 'are succesffully exported, please check your directory\n')

#Open the directory automatically once site drawings are completed
#drawingLoc = "M:\ArcGIS Development\Site Drawing Automation\Index Data\Site Drawings PDF"
#os.startfile(drawingLoc)


