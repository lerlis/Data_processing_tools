# -*- coding: utf-8 -*-
import os
import numpy as np
import openpyxl

class WindExtractor:
    def __init__(self, path):
        self.WindFilePath = path
        self.dirs = os.listdir(self.WindFilePath)
        self.whole_data = None
        self.last_ulogname = None
        self.now_ulogname = None

    def filefinder(self, ulogname):
        ulogname = self.ulogname2date(ulogname)
        # print(self.dirs)
        self.now_ulogname = ulogname
        if ulogname in self.dirs:
            windxlspath = self.WindFilePath + '//' + ulogname
            return windxlspath
        else:
            return 100
        
    def ulogname2date(self, ulogfile_name):
        process_name = ulogfile_name.split('-')
        date_name = '0' + process_name[1] + process_name[2]
        # print(date_name)
        return date_name

    def file_reader(self, xlspath):
        if self.last_ulogname == self.now_ulogname:
            pass
        else:
            xls_list = os.listdir(xlspath)
            # print(xls_list)
            self.whole_data = []
            wind_title = ['采集时间', '风速', '风级', '风向角度', '风向']
            self.whole_data.append(wind_title)
            for i in range(len(xls_list)):
                data_file = xlspath + "//" + xls_list[i]
                # print(data_file)
                wb = openpyxl.load_workbook(data_file)
                sheet = wb.worksheets[0]
                all_data = []
                for row in sheet.iter_rows():
                    row_data = []
                    for cell in row:
                        if cell.value == '':
                            pass
                            flag = 1
                        else:
                            row_data.append(cell.value)
                    if row_data == wind_title or flag == 1:
                        flag = 0
                    else:
                        all_data.append(row_data)
                self.whole_data.extend(all_data)
            self.last_ulogname = self.now_ulogname

    def wind_data_selector(self, ulogtime, timer):
        start_time = ulogtime[0]
        end_time = ulogtime[1]
        time_bias_s = timer.CalcualteTimebiasPX4(start_time)
        start_time_ros = timer.PX4transROS(time_bias_s)
        time_bias_e = timer.CalcualteTimebiasPX4(end_time)
        end_time_ros = timer.PX4transROS(time_bias_e)
        print(timer.RosTimeStamp2Date(start_time_ros), timer.RosTimeStamp2Date(end_time_ros))
        print(round(start_time_ros//1e9), round(end_time_ros//1e9))
        selected_data = []
        Wind_title = ['timestamp', 'sampletime', 'wind_speed', 'wind_scale', 'wind_direction_angle', 'wind_direction']
        selected_data.append(Wind_title)
        start_mode = 0
        for i in range(1, len(self.whole_data)-1):
            time_now = timer.Date2RosTimeStamp(self.whole_data[i][0])
            if i == (len(self.whole_data) - 1):
                break
            time_next = timer.Date2RosTimeStamp(self.whole_data[i+1][0])
            if start_mode:
                row_data = [time_now * 1e9]
                row_data.extend(self.whole_data[i])
                selected_data.append(row_data)
            if time_now <= round(start_time_ros//1e9) and time_next >= round(start_time_ros//1e9):
                start_mode = 1
            if time_now <= round(end_time_ros//1e9) and time_next >= round(end_time_ros//1e9):
                start_mode = 0
                break
        return selected_data

        
if __name__ == "__main__":
    path = 'F://健康评估//数据集论文//实飞//怀来实飞数据//wind'
    WEcase = WindExtractor(path)
    ulogfile_name = 'log_7_2023-5-25-10-48-42.ulg'
    
    ulogtime = [146207571, 232620627]
    xlspath = WEcase.filefinder(ulogfile_name)
    if xlspath != 100:
        WEcase.file_reader(xlspath)
        # selectedDayWind = WEcase.wind_data_selector(ulogtime)
    else:
        print("No such wind data satisfied! Please re-check!")
    
