import numpy as np
import time
import csv
import pandas as pd
import re

from timetrans import TimeBridgeofPX4andROS
# from windextract import WindExtractor

class CSVFile_extractor:
    def __init__(self, input_path):
        self.data_file_path = input_path
        
    def DataFromCSV(self, file_name, labels, labels_f, path):
        target_path = self.data_file_path + '//' + path
        target_file_path = target_path + '//' + file_name
        all_data = []
        with open(target_file_path, mode='r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            header_row = next(csvreader)
            all_data.append(labels)
            # print(header_row)
            col_index = self.label_index_mate(labels, header_row)
            # print(col_index)
            for row in csvreader:
                row_data = []
                for j in range(len(col_index)):
                    trans_data = self.transfer_data_type(row[col_index[j]], labels_f[j])
                    row_data.append(trans_data)
                all_data.append(row_data)
            if len(all_data[1]) == 1:
                all_data = [i for j in range(len(all_data)) for i in all_data[j]]
            return all_data

    def DataFromCSV_Panda(self, file_name, labels, path):
        target_path = self.data_file_path + '//' + path
        target_file_path = target_path + '//' + file_name
        # df = pd.read_csv(target_file_path, dtype={'col1': int, 'col8': int})
        df = pd.read_csv(target_file_path)
        # print(df.columns.to_list())
        # Timelist = df['frame_id'].to_list()
        # print(type(Timelist[2]))
        # print(len(df.values))
        header = df.columns.to_list()
        col_index = self.label_index_mate(labels, header)
        all_data = []
        all_data.append(labels)
        for i in range(len(df.values)):
            row_data = []
            for j in range(len(col_index)):
                row_data.append(df.values[i][col_index[j]])
            all_data.append(row_data)
        if len(all_data[1]) == 1:
            all_data = [i for j in range(len(all_data)) for i in all_data[j]]
        return all_data

    def label_index_mate(self, labels, header):
        col_index = []
        for i in range(len(labels)):
            index = header.index(labels[i])
            col_index.append(index)
        return col_index

    def get_start_end_time(self, arm_data):
        data_len = len(arm_data)
        first_time = arm_data[1][0]
        last_time = arm_data[data_len-1][0]
        for i in range(1, 10):
            if (arm_data[i][1] != arm_data[i+1][1]) and arm_data[i][1] == '0':
                first_time = arm_data[i+1][0]
                print("New start time!!!")
        for i in range(data_len-1, data_len-11, -1):
            if (arm_data[i][1] != arm_data[i-1][1]) and arm_data[i][1] == '0':
                last_time = arm_data[i-1][0]
                print("New end time!!!")
        return [int(first_time), int(last_time)]

    def transfer_data_type(self, data, format):
        if format == 'str':
            data = str(data)
        elif format == 'int':
            data = int(data)
        elif format == 'float':
            data = float(data)
        elif format == 'listf':
            data = re.findall(r'-?\d+\.?[0-9]*', data)
            data = [float(i) for i in data]
        elif format == 'listi':
            data = re.findall(r'-?\d+\.?[0-9]*', data)
            data = [int(i) for i in data]
        else:  # types do not need to be changed, can be expressed as 'stay' in format!
            pass
        return data

    def generate_CSV_data(self, DataArray, new_file_name):
        new_file_path = self.data_file_path + '//' + new_file_name
        with open(new_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(DataArray)


if __name__ == "__main__":
    Data_path = 'F://健康评估//数据集论文//实飞//整理数据//200//51_2'
    CFEcase = CSVFile_extractor(Data_path)
    PX4_file_folder = 'log_2_2023-5-30-14-32-00'
    ROS_file_folder = 'rfly_real_2023-05-30-14-21-00'
    file_name = 'log_2_2023-5-30-14-32-00_actuator_armed_0.csv'
    labels = ['timestamp', 'armed', 'manual_lockdown', 'force_failsafe']
    labels_format = ['int', 'int', 'int', 'int']
    ArmData = CFEcase.DataFromCSV(file_name, labels, labels_format, PX4_file_folder)
    ulogtime = CFEcase.get_start_end_time(ArmData)
    print(ulogtime)
    R_file_name = '_slash_mavros_slash_timesync_status.csv'
    R_labels = ['rosbagTimestamp', 'remote_timestamp_ns']
    R_labels_format = ['int', 'int']
    TimesyncData = CFEcase.DataFromCSV(R_file_name, R_labels, R_labels_format, ROS_file_folder)
    start_time = TimesyncData[1]
    print(start_time)
    TimeTool = TimeBridgeofPX4andROS(ros_t=start_time[0], px4_t=start_time[1]//1000)

    # Wind correlation
    # Wind_path = 'F://健康评估//数据集论文//实飞//怀来实飞数据//wind'
    # WEcase = WindExtractor(Wind_path)
    # ulogfile_name = PX4_file_folder + '.ulg'
    # xlspath = WEcase.filefinder(ulogfile_name)
    # if xlspath != 100:
    #     WEcase.file_reader(xlspath)
    #     selectedDayWind = WEcase.wind_data_selector(ulogtime, TimeTool)
    #     print(selectedDayWind)
    #     CFEcase.generate_CSV_data(selectedDayWind, 'wind_data.csv')
    # else:
    #     print("No such wind data satisfied! Please re-check!")