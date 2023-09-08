# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.

import os
import pandas as pd
import json
import openpyxl
import time

ProjectPath = os.path.dirname(__file__)

def TimeStamp_remove(header):
    if header[0] == 'timestamp' or header[0] == 'rosbagTimestamp':
        key_name = header[0]
        header.remove(key_name)
    return header

def file_name_extractor(name):
    lst = name.split(".")
    llst = lst[0].split("_")
    llst = llst[3:]
    new_name = ''
    for i in range(len(llst)):
        new_name = new_name + '_' + llst[i]
    return new_name

def remove_file_name_suffix(name):
    lst = name.split(".")
    return lst[0]

def Generate_real_flight_dict(PX4_path, ROS_path, generate_path):
    # Generate PX4 data dict
    judge_ulog_trans(PX4_path)
    time.sleep(5)
    listOfCSVFiles = [f for f in os.listdir(PX4_path) if f[-4:] == ".csv"]  # get list of only CSV files in current dir.
    # print(listOfCSVFiles)
    dict_whole = {}
    list_len = len(listOfCSVFiles)
    for i in range(list_len):
        target_file_path = PX4_path + '\\' + listOfCSVFiles[i]
        df = pd.read_csv(target_file_path)
        header = df.columns.to_list()
        header = TimeStamp_remove(header)
        dict_single = dict(zip(header, [0 for _ in range(len(header))]))
        dict_case = {file_name_extractor(listOfCSVFiles[i]): dict_single}
        dict_whole.update(dict_case)
    # print(dict_whole)
    dict_data = {'Real_PX4': dict_whole}
    # Transfer dict type into JSON.
    json.dump(dict_data, open(generate_path + 'data_real_PX4.json', 'w'), indent=4)
    # Generate ROS data dict
    listOfCSVFiles = [f for f in os.listdir(ROS_path) if f[-4:] == ".csv"]  # get list of only CSV files in current dir.
    dict_whole = {}
    list_len = len(listOfCSVFiles)
    for i in range(list_len):
        target_file_path = ROS_path + '\\' + listOfCSVFiles[i]
        df = pd.read_csv(target_file_path)
        header = df.columns.to_list()
        header = TimeStamp_remove(header)
        dict_single = dict(zip(header, [0 for _ in range(len(header))]))
        dict_case = {remove_file_name_suffix(listOfCSVFiles[i]): dict_single}
        dict_whole.update(dict_case)
    dict_data = {'Real_ROS': dict_whole}
    # Transfer dict type into JSON.
    json.dump(dict_data, open(generate_path + 'data_real_ROS.json', 'w'), indent=4)


def judge_ulog_trans(path):
    listOfCSVFiles = [f for f in os.listdir(path) if f[-4:] == ".csv"]  # get list of only CSV files in current dir.
    if len(listOfCSVFiles) == 0:
        os.chdir(path)
        os.system("for %i in (*); do ulog2csv %i")
        os.chdir(ProjectPath)
        print('Transformation Finished !!!')
    else:
        print('Already Transformed')
    

def Generate_SHIL_flight_dict(PX4_path, GTD_path, generate_path):
    # Generate PX4 data dict
    judge_ulog_trans(PX4_path)
    time.sleep(5)
    listOfCSVFiles = [f for f in os.listdir(PX4_path) if f[-4:] == ".csv"]  # get list of only CSV files in current dir.
    dict_whole = {}
    list_len = len(listOfCSVFiles)
    for i in range(list_len):
        target_file_path = PX4_path + '\\' + listOfCSVFiles[i]
        df = pd.read_csv(target_file_path)
        header = df.columns.to_list()
        header = TimeStamp_remove(header)
        dict_single = dict(zip(header, [0 for _ in range(len(header))]))
        dict_case = {file_name_extractor(listOfCSVFiles[i]): dict_single}
        dict_whole.update(dict_case)
    # print(dict_whole)
    dict_data = {'SIL_PX4': dict_whole}
    # Transfer dict type into JSON.
    json.dump(dict_data, open(generate_path + 'data_SIL_PX4.json', 'w'), indent=4)
    dict_data = {'HIL_PX4': dict_whole}
    json.dump(dict_data, open(generate_path + 'data_HIL_PX4.json', 'w'), indent=4)
    # Generate Ground Truth data dict
    listofXLSXFiles = [f for f in os.listdir(GTD_path) if f[-5:] == ".xlsx"]  # get list of only xlsx files in current dir.
    dict_whole = {}
    list_len = len(listofXLSXFiles)
    for i in range(list_len):
        target_file_path = GTD_path + '\\' + listofXLSXFiles[i]
        wb = openpyxl.load_workbook(target_file_path)
        sheet = wb.worksheets[0]
        header = []
        for row in sheet[1]:
            header.append(row.value)
        dict_single = dict(zip(header, [0 for _ in range(len(header))]))
        dict_case = {remove_file_name_suffix(listofXLSXFiles[i]): dict_single}
        dict_whole.update(dict_case)
    dict_data = {'SIL_Ground_Truth_Data': dict_whole}
    # Transfer dict type into JSON.
    json.dump(dict_data, open(generate_path + 'data_SIL_GTD.json', 'w'), indent=4)
    dict_data = {'HIL_Ground_Truth_Data': dict_whole}
    json.dump(dict_data, open(generate_path + 'data_HIL_GTD.json', 'w'), indent=4)  


if __name__ == "__main__":
    """
    mode = 0 refers to HIL or SIL,
    and mode = 1 refers to Real
    """
    mode = 1
    if mode == 0:  # Generate data dict used for SIL and HIL flight data
        PX4_path = './SampleData\\HIL\\acce\\TestCase_1_2400000000\\Log'
        GTD_path = './SampleData\\HIL\\acce\\TestCase_1_2400000000\\TrueData'
        generate_path = './'
        Generate_SHIL_flight_dict(PX4_path, GTD_path, generate_path)
    elif mode == 1:  # Generate data dict used for real flight data
        PX4_path = './SampleData\\Real\\hover\\12_1\\log_6_2023-5-17-15-43-36'
        ROS_path = './SampleData\\Real\\hover\\12_1\\rfly_real_2023-05-17-15-41-51'
        generate_path = './'
        Generate_real_flight_dict(PX4_path, ROS_path, generate_path)