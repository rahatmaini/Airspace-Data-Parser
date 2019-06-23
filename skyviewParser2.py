import xml.etree.ElementTree as ET
from gmplot import gmplot
import webbrowser
import random
import copy

gplotLat=0
gplotLong=0
routeType=""
routeID=""
routeIDs=[] #avoid duplicates
routeStructureWaypoints=[] #just waypoints
routeTransitionLegs=[] #list of transition waypoints


def getAirportLatLong():
    global gplotLat,gplotLong
    for airport in root.findall("./SkyViewAIS/Airports/Airport"):
        if (airport.find("Identifier").text==userInput):
            gplotLat=float(airport.find("Latitude").text)
            gplotLong=float(airport.find("Longitude").text)
            return

def getNumberOfRoutes():
    routeNumber=0
    for route in root.findall("./SkyViewAIS/Routes/Route"):
        routeType=route.find('RouteType').text
        routeID=route.find('Identifier').text
        try:
            airportID=route.find('AirportID').text
            if ((routeType=="STAR" or routeType=="RNAV SID" or routeType=="RNAV STAR" or routeType=="SID" or routeType=="Approach") and airportID==userInput and routeID not in routeIDs):
                routeNumber+=1
        except:
            continue
    return routeNumber

def getRouteTypeAndID():
    global routeID, routeType
    for route in root.findall("./SkyViewAIS/Routes/Route"):

        routeType=route.find('RouteType').text
        routeID=route.find('Identifier').text
        try:
            airportID=route.find('AirportID').text
            if ((routeType=="STAR" or routeType=="RNAV SID" or routeType=="RNAV STAR" or routeType=="SID" or routeType=="Approach") and airportID==userInput and routeID not in routeIDs):
                routeIDs.append(routeID)
                break
        except:
            continue
    return

def populateStructureWaypoints():
    global routeStructureWaypoints
    for route in root.findall("./SkyViewAIS/Routes/Route"):
    
        try:
            thisRouteID=route.find('Identifier').text
            if (thisRouteID==routeID):
                for routeStructure in route.find('RouteStructure'):
                    for routeLeg in routeStructure.findall("RouteWaypoint"):
                        routeStructureWaypoints.append(routeLeg.find("Identifier").text)
        except:
            continue

def populateTransitionWaypoints():
    global routeTransitionLegs
    for route in root.findall("./SkyViewAIS/Routes/Route"):
    
        try:
            thisRouteID=route.find('Identifier').text
            if (thisRouteID==routeID):
                for testing in route.findall('RouteTransition'):
                    for testing2 in testing: #find is giving first route transition waypoints, findall does nothing
                        #print (routeTransition) 
                        for routeLeg in testing2.findall("RouteWaypoint"):
                            routeTransitionLegs.append(routeLeg.find("Identifier").text)
                    routeTransitionLegs.append(" ")
                    
        except:
            continue

def convertWaypointsToLatLongTuple(listToConvert):
    x=0
    while x<len(listToConvert):
        if (listToConvert[x]==" " and x!=len(listToConvert)-1):
            x+=1
        if (listToConvert[x]==" " and x==len(listToConvert)-1):
            break
        for waypoint in root.findall("./SkyViewAIS/Airports/Airport"):
            
            if (waypoint.find("Identifier").text==listToConvert[x]):
                listToConvert[x]=(float(waypoint.find("Latitude").text),float(waypoint.find("Longitude").text))
                x+=1
                if (x==len(listToConvert)):
                    return (listToConvert)
        for waypoint in root.findall("./SkyViewAIS/Navaids/Navaid"):
            
            if (waypoint.find("Identifier").text==listToConvert[x]):
                listToConvert[x]=(float(waypoint.find("Latitude").text),float(waypoint.find("Longitude").text))
                x+=1
                if (x==len(listToConvert)):
                    return (listToConvert)
        for waypoint in root.findall("./SkyViewAIS/Waypoints/Waypoint"):
            if (waypoint.find("Identifier").text==listToConvert[x]):
                listToConvert[x]=(float(waypoint.find("Latitude").text),float(waypoint.find("Longitude").text))
                x+=1
                if (x==len(listToConvert)):
                    return (listToConvert)
    return (listToConvert)



root = ET.parse('AirspaceData_usa_20190328_000000.xml')

userInput=input("Routes in/out of which airport?").upper()

getAirportLatLong()
gmapAll = gmplot.GoogleMapPlotter(gplotLat, gplotLong, 8)
gmapSingle = gmplot.GoogleMapPlotter(gplotLat, gplotLong, 7)


i=0
z=0
listOfColors=["black","silver","gray","maroon","red","purple","fuchsia","green","lime","olive","yellow","navy","blue","teal","aqua"]
while (i<getNumberOfRoutes()):
    getRouteTypeAndID() #at this point have one route type and ID
    populateStructureWaypoints() #at this point have all waypoints for the structure for that route
    populateTransitionWaypoints() #have list of all transitions (separated by empty element in list)
    
    displayStructureWaypoints=copy.deepcopy(routeStructureWaypoints)
    displayTransitionLegs=copy.deepcopy(routeTransitionLegs)
    routeStructureWaypoints=convertWaypointsToLatLongTuple(routeStructureWaypoints)
    routeTransitionLegs=convertWaypointsToLatLongTuple(routeTransitionLegs)

    
    if (len(routeStructureWaypoints) != 0):
        waypointLats, waypointLons = zip(*routeStructureWaypoints)
        gmapAll.plot(waypointLats, waypointLons, listOfColors[random.randint(0,len(listOfColors)-1)] , edge_width=6)
        gmapSingle.plot(waypointLats, waypointLons, "white" , edge_width=6)


    routeStructureWaypoints=[]
    #turn structure into lat longs, plot it

    if (len(routeTransitionLegs)!=0):
        listToZipUp=[]
        while (len(routeTransitionLegs)!=0):
            if (routeTransitionLegs[0]!=" "):
                listToZipUp.append(routeTransitionLegs[0])
                del routeTransitionLegs[0]
            if (routeTransitionLegs[0]==" "):
                waypointLats, waypointLons = zip(*listToZipUp)
                auto=listOfColors[random.randint(0,len(listOfColors)-1)]
                gmapSingle.plot(waypointLats, waypointLons, auto, edge_width=5)
                del routeTransitionLegs[0]
                listToZipUp=[]
    print (routeType, routeID, "Structure: ", displayStructureWaypoints, "Transitions: ", displayTransitionLegs)
    if input("Print this route?(y/n)")=="y":
        if (":" in routeID):
            fileName=routeID[0:4]+".html"
        else:
            fileName=routeID+".html"
        gmapSingle.draw(fileName)
        webbrowser.open(fileName)


gmapAll.draw("my_map.html")

userInput=input("Print all map?(y/n)")

if userInput=="y":
    webbrowser.open("my_map.html")









