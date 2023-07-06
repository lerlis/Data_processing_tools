import numpy as np
import time
import csv
import pandas as pd

from timetrans import TimeBridgeofPX4andROS
from windextract import WindExtractor


class CSVFile_extractor:
    def __init__(self, input_path):
        self.data_file_path = input_path
        
    def DataFromCSV(self, file_name, labels, path):
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
                    row_data.append(row[col_index[j]])
                all_data.append(row_data)
            all_data = np.squeeze(all_data)
            return all_data.tolist()

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
        all_data = np.squeeze(all_data)
        return all_data.tolist()

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


if __name__ == "__main__":
    Data_path = 'F://健康评估//数据集论文//实飞//怀来实飞数据//200//0525'
    CFEcase = CSVFile_extractor(Data_path)
    PX4_file_folder = 'log_0_2023-5-25-10-07-52'
    ROS_file_folder = 'rfly_real_2023-05-25-10-06-20'
    file_name = 'log_0_2023-5-25-10-07-52_actuator_armed_0.csv'
    labels = ['timestamp', 'armed', 'manual_lockdown', 'force_failsafe']
    ArmData = CFEcase.DataFromCSV(file_name, labels, PX4_file_folder)
    ulogtime = CFEcase.get_start_end_time(ArmData)
    print(ulogtime)
    R_file_name = '_slash_mavros_slash_timesync_status.csv'
    R_labels = ['rosbagTimestamp', 'remote_timestamp_ns']
    TimesyncData = CFEcase.DataFromCSV_Panda(R_file_name, R_labels, ROS_file_folder)
    start_time = TimesyncData[1]
    TimeTool = TimeBridgeofPX4andROS(ros_t=start_time[0], px4_t=start_time[1]//1000)

    # Wind correlation
    Wind_path = 'F://健康评估//数据集论文//实飞//怀来实飞数据//wind'
    WEcase = WindExtractor(Wind_path)
    ulogfile_name = PX4_file_folder + '.ulg'
    xlspath = WEcase.filefinder(ulogfile_name)
    if xlspath != 100:
        WEcase.file_reader(xlspath)
        selectedDayWind = WEcase.wind_data_selector(ulogtime, TimeTool)
    else:
        print("No such wind data satisfied! Please re-check!")
    print(selectedDayWind)
