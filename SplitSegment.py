import arcpy
import os
import json
import pythonaddins

def main():
    pass

if __name__== '__main__':
    main()

# Configure current layer file as main working file
mxd = arcpy.mapping.MapDocument("CURRENT")
mxdLocation = os.path.dirname(mxd.filePath)

# Clean polygon layer if exists
polygonLayer = "M:\ArcGIS Development\Site Drawing Automation\POLYGON_DDP.shp"
if os.path.exists(polygonLayer):
    arcpy.Delete_management(polygonLayer)
    arcpy.AddMessage("\nPolygon Layer exists, would be deleted \n")
    
# GUI Interface to create indexed polygons
polylineDDP = arcpy.GetParameterAsText(0)               # Polyline DDP
lengthDDP = arcpy.GetParameterAsText(1)                 # DDP length for polygon
widthDDP = arcpy.GetParameterAsText(2)                  # Data width for polygon
scaleDDP = arcpy.GetParameterAsText(3)                  # Data scale
outfileDDP = arcpy.GetParameterAsText(4)                # output file directory

# Check if anypolyline inside the the layer
polylineCount = arcpy.GetCount_management(polylineDDP)
if polylineCount == 0:
    arcpy.AddMessage("\nNo data in polyline, please draw using editor tool. \n")
    quit()
    
# Compute the segments
arcpy.StripMapIndexFeatures_cartography (polylineDDP, outfileDDP, "NO_USEPAGEUNIT", scaleDDP, lengthDDP, widthDDP,"HORIZONTAL",0)

# Load shapefile result to geodatabase
out_location = r"M:\ArcGIS Development\Site Drawing Automation\Index Data\DDP.gdb\POLYGON_DDP"

arcpy.DeleteFeatures_management(out_location)
arcpy.Append_management(outfileDDP, out_location)
arcpy.AddMessage("\nThe Polygon data is successfully appended to geodatabase.\n")
arcpy.AddMessage("\nMake sure you Enable the DDP and load the drawing template. \n")

# Delete shapefile
if os.path.exists(outfileDDP):
    arcpy.Delete_management(outfileDDP)
