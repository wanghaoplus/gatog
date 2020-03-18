# -*- coding: utf-8 -*-
import os
import time
import numpy as np
import colorsys
from aw.utils.nmeanalysis.ActionDB import ActionDB
from aw.utils.nmeanalysis.AresInput import PRINTI

class creatHigeo2KML(object):
    def __init__(self, resourceDB, deviceInfo):
        self.resourceDB = ActionDB(resourceDB)
        self.deviceDict = deviceInfo
        
    def convertPosition2Kml(self, kmlPath):
        if not os.path.exists(kmlPath):
            os.mkdir(kmlPath)
        elif not os.path.isdir(kmlPath):
            return False, "kmlpath is not dir[{}]".format(kmlPath)
        techList = {}
        for info in self.deviceDict:
            device = info["tech"]
            Type = info.get("type", None)
            if Type == "test" or Type == "competitive" or Type == "standard":
                techList.setdefault(device, info)
            else:
                return False, "deviceInfo[{}] has something wrong".format(self.deviceDict)
                
        kmlname = os.path.join(kmlPath, "HDBD_" + time.strftime('_%Y%m%d_%H%M%S', time.localtime(time.time())) + ".kml")
    
        with open(kmlname, 'w') as kml:
            colorList = self.__get_spaced_colors(len(techList))
            colorOfTypeDict = dict(zip(techList.keys(), colorList))
    
            self.__writeKmlStart(kml, kmlname, colorOfTypeDict)
    
            self.__writeKmlFolderStart(kml, "HDBD")
    
            # ----------------------------------------------#
            otherTrackList = ["UTC", "longitude", "latitude", "speed", "heading", "ACC" ]
            for device_type, value in techList.items():

                self.__writeKmlFolderStart(kml, device_type)
                self.__writeKmlPolyStart(kml, "%sPath" % device_type, "Path", "")
                
                data = self.resourceDB.getcolomFormDB(device_type, otherTrackList)
                for row in data:
                    self.__writeKmlPolyPoint(kml, row[2], row[1])
                self.__writeKmlPolyEnd(kml)
                # Point
                self.__writeKmlFolderStart(kml, "Point")

                for row in data:
                    source = ""
                    if len(row) == 7:
                        source = row[6]
                    self.__writePoint(kml, self.__fixStrLen(row[0], 8), row[2], row[1], row[3], row[4],
                               row[5], True, \
                               "", source, "", "", colorOfTypeDict[device_type])
                self.__writeKmlFolderEnd(kml)  # Point
                # Uncertainty
                self.__writeKmlFolderStart(kml, "Uncertainty")

                for row in data:
                    self.__writeUncertainty(kml, self.__fixStrLen(row[0], 8), row[2], row[1], row[5])
                self.__writeKmlFolderEnd(kml)  # Uncertainty
                self.__writeKmlFolderEnd(kml)  # tech
    
            # ----------------------------------------------#
            self.__writeKmlFolderEnd(kml)  # HiGeo
    
            self.__writeKmlEnd(kml)
    
            kml.close()
        return True, kmlname
            
    def __get_spaced_colors(self, N):
            if N == 1:
                return ['ffffff']
            # HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in xrange(N)]
            HSV_tuples = [(x * 1.0 / N, 1, 1) for x in range(N)]
            hex_out = []
            for rgb in HSV_tuples:
                rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
                hex_out.append("".join(map(self.__int2hex, rgb)))
            return hex_out
        
    def __int2hex(self, data):
        tmp = hex(data)
        if len(tmp) == 3:
            return "0" + tmp[-1]
        else:
            return tmp[2:]
        
    def __writeKmlStart(self, kml, kmlname, colorOfTypeDict):
        # kml.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        #           "<kml xmlns:='http://earth.google.com/kml/2.1'>\n"
        #           "  <Document>\n"
        #           "  <name>{0}</name>\n"
        #           "  <Style id=\"gpsPin\"><IconStyle><scale>0.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle-lv.png</href></Icon></IconStyle></Style>\n"
        #           "  <Style id=\"vdrPin\"><IconStyle><scale>0.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle-lv.png</href></Icon></IconStyle></Style>\n"
        #           "  <Style id=\"finalPin\"><IconStyle><scale>0.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle-lv.png</href></Icon></IconStyle></Style>\n"
        #           "  <Style id=\"wlanPin\"><IconStyle><scale>0.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-circle-lv.png</href></Icon></IconStyle></Style>\n"
        #           "  <Style id=\"gpsPath\"><LineStyle><color>{1}</color><width>4</width></LineStyle><PolyStyle><color>{1}</color></PolyStyle></Style>\n"
        #           "  <Style id=\"wlanPath\"><LineStyle><color>{2}</color><width>4</width></LineStyle><PolyStyle><color>{2}</color></PolyStyle></Style>\n"
        #           "  <Style id=\"finalPath\"><LineStyle><color>{3}</color><width>4</width></LineStyle><PolyStyle><color>{3}</color></PolyStyle></Style>\n"
        #           "  <Style id=\"vdrPath\"><LineStyle><color>{4}</color><width>4</width></LineStyle><PolyStyle><color>{4}</color></PolyStyle></Style>\n"
        #           "  <Style id=\"Uncertainty\"><LineStyle><color>{5}</color><width>2.00000</width>    </LineStyle></Style>\n".format(
        #     kmlname, gpsColor, wlanColor, finalColor, vdrColor, whiteColor))
    
    
#        kml_html_template = """
#                 <?xml version=\"1.0\" encoding=\"UTF-8\"?>
#                 <kml xmlns:='http://earth.google.com/kml/2.1'>
#                 <Document>
#                 <name>{0}</name>
#                 {1}
#                 {2}
#                 <Style id=\"Uncertainty\"><LineStyle><color>ffffffff</color><width>2.00000</width>    </LineStyle></Style>
#                 """
    
        kml_html_pin_template = "<Style id=\"%sPin\"><IconStyle><scale>0.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle-lv.png</href></Icon></IconStyle></Style>\n"
        pin_str = ""
        for index, Type in enumerate(colorOfTypeDict.keys()):
            if index > 0 :
                pin_str += "  " + kml_html_pin_template % Type
            else:
                pin_str += kml_html_pin_template % Type
    
        kml_html_path_template = "<Style id=\"%sPath\"><LineStyle><color>ff%s</color><width>4</width></LineStyle><PolyStyle><color>ff%s</color></PolyStyle></Style>\n"
        path_str = ""
        for index, Type in enumerate(colorOfTypeDict.keys()):
            color = colorOfTypeDict[Type]
            if index > 0 :
                path_str += "  " + (kml_html_path_template % (Type, color, color))
            else:
                path_str += (kml_html_path_template % (Type, color, color))
    
        # kml_html_template = kml_html_template.format(kmlname, pin_str, path_str)
        # kml.write(kml_html_template)
    
        kml.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                  "<kml xmlns:='http://earth.google.com/kml/2.1'>\n"
                  "  <Document>\n"
                  "  <name>{0}</name>\n"
                  "  {1}"
                  "  {2}"
                  "  <Style id=\"Uncertainty\"><LineStyle><color>ffffffff</color><width>2.00000</width>    </LineStyle></Style>\n".format(
            kmlname, pin_str, path_str))
        
    def __writeKmlFolderStart(self, kml, name, visible=True):
        kml.write("<Folder>\n"
                  "<name>{0}</name>\n"
                  "<visibility>{1}</visibility>\n".format(name, "1" if visible else "0"))
        
    def __writeKmlPolyStart(self, kml, style, name, desc, visible=True):
        kml.write("<Placemark>\n"
                  "<name>{0}</name>\n"
                  "<description>{1}</description>\n"
                  "<styleUrl>{2}</styleUrl>\n"
                  "<visibility>{3}</visibility>\n"
                  "<LineString><extrude>0</extrude><tessellate>1</tessellate><altitudeMode>clampToGround</altitudeMode>\n"
                  "<coordinates>\n".format(name, desc, style, "1" if visible else "0"))
        
    def __writeKmlPolyPoint(self, kml, lat, lon):
        kml.write("{0},{1}\n".format(lon, lat))
        
    def __writeKmlPolyEnd(self, kml):
        kml.write("</coordinates>\n</LineString></Placemark>\n")
        
    def __writePoint(self, kml, time, lat, lon, speed, heading, acc, arrow, tech, source, Cuse, age, color):
        color = "ff" + color
        pin = tech
    
        desc = "Time: {0}\nLat: {1}\nLon: {2}\nAcc: {3}\nSpeed: {9}\nHeading: {4}\nTechnology: {5}\nSource: {6}\nUsedWiFi: {7}\nScanAge: {8}\n".format(
            time,
            lat,
            lon,
            acc,
            heading,
            tech,
            source,
            Cuse, age,
            speed
        )
        timestamp = time.replace(" ", "T") + 'Z'
    
        if (arrow == True) & (heading != ''):
            rotate = str((180.0 + float(heading)) % 360)
            headingDes = "<Style><IconStyle><scale>0.4</scale><color>{1}</color><heading>{0}</heading><Icon><href>http://maps.google.com/mapfiles/kml/shapes/arrow.png</href></Icon></IconStyle></Style>\n".format(
                rotate, color)
        else:
            # headingDes = "<Style><IconStyle><scale>0.3</scale><Icon><href>http://maps.google.com/mapfiles/kml/paddle/{0}</href></Icon></IconStyle></Style>\n".format(pointIcon)
            headingDes = "<Style><IconStyle><scale>0.3</scale><color>{0}</color><Icon><href>http://hi3ms-image.huawei.com/hi/staticimages/hi3msf/images/2017/0522/20/5922daf4051ef.png</href></Icon></IconStyle></Style>\n".format(color)
    
        self.__writeKmlPlaceMark(kml, pin, "", desc, lat, lon, acc, timestamp, headingDes)
        
    def __writeKmlFolderEnd(self, kml):
        kml.write("</Folder>\n")
        
    def __writeUncertainty(self, kml, time, lat, lon, acc):
        timestamp = time.replace(" ", "T") + 'Z'
        self.__writeKmlUncertainty(kml, lat, lon, acc, timestamp)
        
    def __writeKmlEnd(self, kml):
        kml.write("</Document></kml>\n")
        
    def __writeKmlUncertainty(self, kml, lat, lon, acc, timestamp, visible=False):
        try:
            circle = self.__genCircle(lat, lon, 8, acc)
            kml.write("<Placemark>\n"
                      "<TimeStamp><when>{1}</when></TimeStamp>\n"
                      "<styleUrl>Uncertainty</styleUrl>\n"
                      "<visibility>{0}</visibility>"
                      "<MultiGeometry>\n"
                      "<LineString><coordinates>\n"
                      "{2}"
                      "</coordinates></LineString>\n"
                      "</MultiGeometry>\n"
                      "</Placemark>\n".format("1" if visible else "0", timestamp, circle))
        except Exception as e:
            print(e, lat, lon, acc, timestamp)
        
    def __writeKmlPlaceMark(self, kml, style, name, desc, lat, lon, acc, timestamp, headingDes, visible=True):
        kml.write("<Placemark>\n"
                  "<name>{2}</name>\n"
                  "<TimeStamp><when>{6}</when></TimeStamp>\n"
                  "<description>\n{3}</description>\n"
                  "<styleUrl>{4}</styleUrl>\n"
                  "{7}"
                  "<visibility>{5}</visibility>"
                  "<Point><coordinates>{0},{1}</coordinates></Point>\n"
                  "</Placemark>\n".format(lon, lat, name, desc, style, "1" if visible else "0", timestamp, headingDes))


    def __fixStrLen(self, string, strlen):
        while len(string) < strlen:
            string = '0' + string
        return string
    
    def __genCircle(self, cenLatStr, cenLonStr, polygonN, radiusStr):
        if radiusStr == '':
            radiusStr = 0
        R = 6378137
        polygon = ''
        pi = np.pi
        cenLat = float(cenLatStr)
        cenLon = float(cenLonStr)
        radius = float(radiusStr)
        for i in range(polygonN):
            theta = (2 * pi / polygonN) * i
            deltaX = radius * np.cos(theta)
            deltaY = radius * np.sin(theta)
            Lat = cenLat + (deltaY / R) * (180 / pi)
            Long = cenLon + (deltaX / R) * (180 / pi)
            polygon = polygon + str(Long) + ',' + str(Lat) + '\n'
    
        return polygon


def createKML(resourceDBpath, kmlPath, deviceInfo):
    PRINTI('createKML START')
    creatkml = creatHigeo2KML(resourceDBpath, deviceInfo)
    return creatkml.convertPosition2Kml(kmlPath)


