import traceback
from aw.utils.nmeanalysis.AresInput import PRINTE

class ViewSatelliteInfoStructure(object):
    def __init__(self):
        self.line = None
        self.cno_info_dict = {}  # {"CNO":["SatelliteID",..],}
        self.satellite_info_dict = {}  # {"satelliteID":[Elevation,Azimuth,CNO],...}

    def set_satellite_info(self, line, satellite_info):
        self.line = line
        num_type_satelliteID = float(satellite_info[0])
        str_type_satelliteID = str(num_type_satelliteID)
        if str_type_satelliteID in self.satellite_info_dict.keys():
            return
        self.satellite_info_dict[str_type_satelliteID] = satellite_info[1:]
        
        if satellite_info[3] not in self.cno_info_dict:
            self.cno_info_dict[satellite_info[3]] = []
        self.cno_info_dict[satellite_info[3]].append(str_type_satelliteID)

    def get_satelliteID_list(self):
        return self.satellite_info_dict.keys()
    
    def get_cno_satellite_info(self):
        return self.satellite_info_dict
    
    def get_satellite_count(self):
        return len(self.satellite_info_dict)

    def get_top5_cno_satellite_info(self):
        try:
            top5_cno_satellite_list = []
            if len(self.cno_info_dict) == 0:
                return top5_cno_satellite_list, 0
            cno_list = list(self.cno_info_dict.keys())
            cno_list.sort(reverse=True)
            offset = 5 if len(cno_list) > 5 else len(cno_list)
            cno_list = cno_list[:offset]
            cno_num_type_list = [float(value) for value in cno_list]
            ave_value = round((float(sum(cno_num_type_list)) / len(cno_num_type_list)), 2)
            for cno in cno_list:
                satelliteIDs = self.cno_info_dict.get(cno)
                for satelliteID in satelliteIDs:
                    top5_cno_satellite = []
                    top5_cno_satellite.append(satelliteID)
                    extra_info = self.satellite_info_dict.get(satelliteID)
                    top5_cno_satellite.extend(extra_info)
                    top5_cno_satellite_list.append(top5_cno_satellite)
            return top5_cno_satellite_list, ave_value
        except:
            return self.line, traceback.format_exc()

    def clear(self):
        self.line = None
        self.cno_info_dict = {}  # {"CNO":["SatelliteID",..],}
        self.satellite_info_dict = {}  # {"satelliteID":[Elevation,Azimuth,CNO],...}


if __name__ == '__main__':
    t = ['1', '3', '2']
    t1 = [float(value) for value in t]
    t.sort(reverse=True)
    a = {}
    print(t1)
