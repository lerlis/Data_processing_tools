# -*- coding: utf-8 -*-
import os
import numpy as np
import openpyxl

from fileprocess import CSVFile_extractor
from timetrans import TimeBridgeofPX4andROS

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
        if len(process_name[1]) == 1:
            process_name[1] = '0' + process_name[1]
        if len(process_name[2]) == 1:
            process_name[2] = '0' + process_name[2]
        date_name = process_name[1] + process_name[2]
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


def check_labels(file_name, labels):
    if file_name[0:3] == labels[0]:
        return 1
    if file_name[0:9] == labels[1]:
        return 2
    if file_name[0:8] == labels[2]:
        return 3
    return 0


if __name__ == "__main__":
    Data_path = 'F://健康评估//数据集论文//实飞//整理数据//680//'
    path_dirs = os.listdir(Data_path)
    ty_labels = ['log', 'rfly_real', 'TestInfo']
    # Wind correlation
    Wind_path = 'F://健康评估//数据集论文//实飞//怀来实飞数据//wind'
    WEcase = WindExtractor(Wind_path)
    for dir in path_dirs:
        process_path = Data_path + dir
        print(process_path)
        CFEcase = CSVFile_extractor(process_path)
        file_name_list = os.listdir(process_path)
        print(file_name_list)
        for i in range(len(file_name_list)):
            return_num = check_labels(file_name_list[i], ty_labels)
            if return_num == 1:
                PX4_file_folder = file_name_list[i]
            elif return_num == 2:
                ROS_file_folder = file_name_list[i]
        file_name = PX4_file_folder + '_actuator_armed_0.csv'
        labels = ['timestamp', 'armed', 'manual_lockdown', 'force_failsafe']
        labels_format = ['int', 'int', 'int', 'int']
        ArmData = CFEcase.DataFromCSV(file_name, labels, labels_format, PX4_file_folder)
        ulogtime = CFEcase.get_start_end_time(ArmData)
        R_file_name = '_slash_mavros_slash_timesync_status.csv'
        R_labels = ['rosbagTimestamp', 'remote_timestamp_ns']
        R_labels_format = ['int', 'int']
        TimesyncData = CFEcase.DataFromCSV(R_file_name, R_labels, R_labels_format, ROS_file_folder)
        start_time = TimesyncData[1]
        TimeTool = TimeBridgeofPX4andROS(ros_t=start_time[0], px4_t=start_time[1]//1000)
        ulogfile_name = PX4_file_folder + '.ulg'
        xlspath = WEcase.filefinder(ulogfile_name)

        if os.path.exists(process_path + '//no_wind_data.txt'):  # 如果有同名的文件，则删除
            os.remove(process_path + '//no_wind_data.txt')

        if xlspath != 100:
            WEcase.file_reader(xlspath)
            selectedDayWind = WEcase.wind_data_selector(ulogtime, TimeTool)
            CFEcase.generate_CSV_data(selectedDayWind, 'wind_data.csv')
            if len(selectedDayWind) == 1:
                print("Has file, but no data")
                with open(process_path + '//no_wind_data.txt', 'w', newline='') as f:
                    sentence = 'This flight has no wind data'
                    f.write(sentence)
        else:
            print("No such wind data satisfied! Please re-check!")
            with open(process_path + '//no_wind_data.txt', 'w', newline='') as f:
                sentence = 'This flight has no wind data'
                f.write(sentence)
            

