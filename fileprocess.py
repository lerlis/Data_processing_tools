# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.
import numpy as np
import csv
import pandas as pd
import re
import os
from scipy.interpolate import interp1d

import matplotlib.pyplot as plt
# from windextract import WindExtractor

class CSVFile_extractor:
    def __init__(self, input_path):
        self.data_file_path = input_path
        self.timetool = None
        self.str2list_flag = 0
        self.changed_index = 0
        self.target_length = 0

    def reset(self):
        self.str2list_flag = 0
        self.changed_index = 0
        self.target_length = 0
        
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
        self.reset()
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
        # for row in df.itertuples():
        #     row_data = []
        #     for i in range(len(row)-1):
        #         row_data.append(row[col_index[i]])
        #     all_data.append(row_data)
        values = df.values
        # all_data += [[values[i][col_i] for col_i in col_index] for i in range(values.shape[0])]
        for i in range(values.shape[0]):
            row_data = []
            for j in range(len(col_index)):
                if type(values[i][col_index[j]]) == str:
                    new_list = self.list_str_check(values[i][col_index[j]])
                    row_data.extend(new_list)
                    # If i == 0, change the header, if not, won't change
                    if i == 0 and self.str2list_flag:
                        self.changed_index = j
                        all_data = self.data_header_adjust(all_data)
                else:
                    row_data.append(values[i][col_index[j]])
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
        """
        This function is used to trans data type of each labels 
        in different files.
        And is invoked by self.DataFromCSV.
        Now, self.DataFromCSV_Panda is more often use.
        """
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

    def list_str_check(self, data):
        if data.find('[') != -1 and data.find(']') != -1:
            new_data = eval(data)
            self.str2list_flag = 1
            self.target_length = len(new_data)
        else:
            new_data = [data]
        return new_data

    def data_header_adjust(self, all_data):
        self.str2list_flag = 0
        name = all_data[0][self.changed_index]
        adjust_name = []
        for i in range(self.target_length):
            adjust_name.append(name + '[' + str(i) + ']')
        all_data[0] = all_data[0][0:self.changed_index] + adjust_name + all_data[0][self.changed_index+1:]
        return all_data

    def generate_data_header(self, label1, label2, info):
        all_file_name = label1 + label2
        header = []
        for i in range(len(all_file_name)):
            for j in range(1, len(info[i])):
                header.append(all_file_name[i] + '_' + info[i][j])
        return header

    def generate_CSV_data(self, DataArray, new_file_name):
        new_file_path = self.data_file_path + '//' + new_file_name
        with open(new_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(DataArray)

    def folder_finder(self):
        dir_list = os.listdir(self.data_file_path)
        # print(dir_list)
        PX4_file_folder = [f for f in dir_list if f[:4] == "log_"]
        ROS_file_folder = [f for f in dir_list if f[:10] == "rfly_real_"]
        return PX4_file_folder[0], ROS_file_folder[0]

    def Ros_file_name_simplify(self, file_name):
        file_num = len(file_name)
        for i in range(file_num):
            if file_name[i].find('_slash_mavros_slash_') != -1:
                file_name[i] = file_name[i][20:]
            elif file_name[i].find('_slash_mavlink_slash_') != -1:
                file_name[i] = file_name[i][21:]
            elif file_name[i].find('_slash_') != -1:
                file_name[i] = file_name[i][7:]
        return file_name

    def find_fly_land_time(self, land_data):
        value = land_data[1][1]
        len_data = len(land_data)
        for i in range(1, len_data):
            if value == land_data[i][1]:
                continue
            else:
                flytime = land_data[i][0]
                break
        fly_index = i
        value = land_data[fly_index+1][2]
        for j in range(fly_index + 1, len_data):
            if value == land_data[j][2]:
                continue
            else:
                landtime = land_data[j][0]
                break
        return int(flytime), int(landtime)

    def cut_data(self, data, begin_time, end_time):
        # First, copy the title
        new_data = [data[0]]
        # Second, get the data within begin and end time
        data_len = len(data)
        for i in range(1, data_len):
            if data[i][0] > begin_time and data[i][0] < end_time:
                new_data.append(data[i])
        return new_data

    def CalcuFreq(self, data):
        data_num = len(data)
        begin_time = data[1][0]
        end_time = data[-1][0]
        constant_time = (end_time - begin_time) / 1e6
        calFreq = data_num / constant_time
        return calFreq

    def freq_adjustment(self, data, target_timevec):
        time_original = data[1:, 0].astype(float)
        len_col = len(data[0])
        stack_flag = 0
        if len_col != 1:
            stack_flag = 1
        for i in range(1, len_col):
            data_col = data[1:, i].astype(float)
            # adjust the frequency of the data
            interpolation_function = interp1d(time_original, data_col)
            new_data_col = interpolation_function(target_timevec)
            if i == 1:
                new_data = new_data_col
                if stack_flag:
                    new_data = np.array([new_data]).T
            else:
                new_data = np.concatenate((new_data, np.array([new_data_col]).T), axis=1)
        return new_data

    def rosdata_timestamp_trans(self, timetool, data):
        data_len = len(data)
        for i in range(1, data_len):
            timenow = data[i][0]
            time_bias = timetool.CalculateTimebiasROS(timenow)
            px4_time = timetool.ROStransPX4(time_bias)
            data[i][0] = px4_time
        return data

    def PX4data_timestamp_trans(self, timetool, data):
        data_len = len(data)
        new_data = np.zeros((data_len, 1), dtype=np.float64)
        for i in range(data_len):
            timenow = data[i]
            time_bias = timetool.CalculateTimebiasPX4(timenow)
            ros_time = timetool.PX4transROS(time_bias)
            new_data[i] = ros_time
        return new_data

    def plot_data(self, time, data):
        """
        time and data needed to be 1-D array vector.
        """
        fig, ax = plt.subplots()
        ax.plot(time, data)
        ax.set_xlabel('time (s)', fontsize=12)
        ax.set_ylabel('adjust_frequency_data', fontsize=12)
        ax.grid()
        plt.show()

if __name__ == "__main__":
    # Wind correlation
    # *******************************************************************
    # Wind process data is moved to windextract.py
    # *******************************************************************
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
    # *******************************************************************
    DataPath = 'F:\\CODE\\Python\\fault_data_process\\SampleData\\Real\\hover\\56_1'
    CFEcase = CSVFile_extractor(DataPath)