# !/usr/bin/env python
# -*- coding:utf8 -*-
# author: hr


from station_version import station_name

class StationInfo(object):
    def __init__(self, station_name):
        self.station_name = station_name
        self.station_dict = {}

    def station_info(self):
        """
        station_version: 1.9063
        """
        station_list = self.station_name.split('@')[1:]
        for station in station_list:
            station_one = station.split("|")
            self.station_dict[station_one[1]] = station_one[2]
        return

    def from_select(self, from_station):
        from_code = self.station_dict[from_station]
        return from_code

    def to_select(self, to_station):
        to_code = self.station_dict[to_station]
        return to_code


    # def main(self):
    #     res = self.station_info()
    #     # re = self.station_select(res, select_sta)
    #     # print(re)

# if __name__ == "__main__":
#     # select_sta = input("请输入")
#     station = StationInfo(station_name)
#     station.main()