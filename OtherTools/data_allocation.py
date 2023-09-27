# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.
import os
import pandas as pd
import shutil

from fileprocess import CSVFile_extractor

class DataAllocator:
    def __init__(self, source_path, target_path):
        self.Data_source_path = source_path
        self.Data_target_path = target_path
        self.filelist = None
        
    def data_reader(self, labels):
        CFEcase = CSVFile_extractor(self.Data_source_path)
        for i in range(len(self.filelist)):
            return_num = self.check_labels(self.filelist[i], labels)
            if return_num == 1:
                PX4_file_folder = self.filelist[i]
                file_name = self.filelist[i] + '_rfly_ctrl_lxl_0.csv'
                px4_labels = ['index']
                time_index = CFEcase.DataFromCSV_Panda(file_name, px4_labels, PX4_file_folder)
                actual_index = self.identify_index(time_index)
                if actual_index == 0:
                    continue
                else:
                    self.folder_creator(actual_index)
                    folder_path = self.Data_source_path + '//' + PX4_file_folder
                    target_path = self.Data_target_path + '//{}_1'.format(actual_index) + '//' + PX4_file_folder
                    shutil.move(folder_path, target_path)
            elif return_num == 2:
                ROS_file_folder = self.filelist[i]
                R_file_name = '_slash_mavros_slash_rfly_ctrl_lxl_slash_send_data.csv'
                R_labels = ['index']
                time_index = CFEcase.DataFromCSV_Panda(R_file_name, R_labels, ROS_file_folder)
                actual_index = self.identify_index(time_index)
                if actual_index == 0:
                    continue
                else:
                    self.folder_creator(actual_index)
                    folder_path = self.Data_source_path + '//' + ROS_file_folder
                    target_path = self.Data_target_path + '//{}_1'.format(actual_index) + '//' + ROS_file_folder
                    shutil.move(folder_path, target_path)
            elif return_num == 3:
                new_path = self.Data_source_path + '//' + self.filelist[i]
                df = pd.read_excel(new_path)
                actual_index = df.columns.to_list()
                actual_index = actual_index[1]
                if actual_index == 0:
                    continue
                else:
                    self.folder_creator(actual_index)
                    folder_path = new_path
                    target_path = self.Data_target_path + '//{}_1'.format(actual_index) + '//' + self.filelist[i]
                    shutil.move(folder_path, target_path)
            else:
                continue

    def identify_index(self, time_index):
        length = len(time_index)
        changed_flag = 0
        for i in range(1, length-1):
            if int(float(time_index[i])) == 0:
                continue
            else:
                changed_flag = 1
                actual_index = int(float(time_index[i]))
                break
        if changed_flag:
            return actual_index
        else:
            return 0
    
    def folder_creator(self, index):
        target_file_name = self.Data_target_path + '//{}_1'.format(index)
        if os.path.exists(target_file_name):
            print('exist!!!')
            print(target_file_name)
        else:
            os.makedirs(target_file_name)
            print("create!!Index:{}".format(index))

    def get_file_list(self):
        self.filelist = os.listdir(self.Data_source_path)
        print(self.filelist)

    def check_labels(self, file_name, labels):
        if file_name[0:3] == labels[0]:
            return 1
        if file_name[0:9] == labels[1]:
            return 2
        if file_name[0:8] == labels[2]:
            return 3
        return 0


if __name__ == "__main__":
    source_file_path = 'F://健康评估//数据集论文//实飞//怀来实飞数据//680//0616'
    target_file_path = 'F://健康评估//数据集论文//实飞//整理数据//680'
    labels = ['log', 'rfly_real', 'TestInfo']
    DAcase = DataAllocator(source_file_path, target_file_path)
    DAcase.get_file_list()
    DAcase.data_reader(labels)
