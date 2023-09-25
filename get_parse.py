# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.

import argparse


def parser_param_process(params):
    # Get original data path
    original_path = params.original_path
    # Get restore path 
    restore_path = params.restore_path
    # Get sub-dataset path
    param = params.sub_dataset
    sub_dataset_path = []
    for i in range(len(param)):
        if param[i] == 0:
            sub_dataset_path = sub_dataset_path_trans(0)
            break
        else:
            sub_dataset_path.append(sub_dataset_path_trans(param[i]))
    # Get fault type path
    param = params.fault_type
    fault_type_path = []
    for i in range(len(param)):
        if param[i] == 0:
            fault_type_path = fault_type_path_trans(0)
        else:
            fault_type_path.append(fault_type_path_trans(param[i]))
    # Get flight status path
    param = params.flight_status
    flight_status_path = []
    for i in range(len(param)):
        if param[i] == 0:
            flight_status_path = flight_status_path_trans(0)
        else:
            flight_status_path.append(flight_status_path_trans(param[i]))
    # Get number of transferred files in each sub-flight-fault structure
    trans_num = params.trans_num
    # Get the data frequency of processed data file.
    # By use SET_FREQUENCY, the data will be unified into the same length
    Set_frequency = params.trans_freq
    return original_path, restore_path, sub_dataset_path, flight_status_path, fault_type_path, trans_num, Set_frequency


def sub_dataset_path_trans(id):
    if id == 1:
        return '/SIL'
    elif id == 2:
        return '/HIL'
    elif id == 3:
        return '/Real'
    elif id == 0:
        return ['/SIL', '/HIL', '/Real']


def fault_type_path_trans(id):
    if id == 1:
        return '/motor'
    elif id == 2:
        return '/propeller'
    elif id == 3:
        return '/low_voltage'
    elif id == 4:
        return '/wind_affect'
    elif id == 5:
        return '/load_lose'
    elif id == 6:
        return '/accelerometer'
    elif id == 7:
        return '/gyroscope'
    elif id == 8:
        return '/magnetometer'
    elif id == 9:
        return '/barometer'
    elif id == 10:
        return '/GPS'
    elif id == 11:
        return '/no_fault'
    elif id == 0:
        return ['/motor', '/propeller', '/low_voltage', '/wind_affect', '/load_lose', '/accelerometer', '/gyroscope', '/magnetometer', '/barometer', '/GPS', '/no_fault']


def flight_status_path_trans(id):
    if id == 1:
        return '/hover'
    elif id == 2:
        return '/waypoint'
    elif id == 3:
        return '/velocity'
    elif id == 4:
        return '/circling'
    elif id == 5:
        return '/acce'
    elif id == 6:
        return '/dece'
    elif id == 0:
        return ['/hover', '/waypoint', '/velocity', '/circling', '/acce', '/dece']


def flight_id_dict(key):
    flight_status_dict = {'/hover': 0, '/waypoint': 1, '/velocity': 2, '/circling': 3, '/acce': 4, '/dece': 5}
    value = flight_status_dict[key]
    return value


def fault_id_dict(key):
    fault_type_dict = {'/motor': 0, '/propeller': 1, '/low_voltage': 2, '/wind_affect': 3, '/load_lose': 4, '/accelerometer': 5, '/gyroscope': 6, '/magnetometer': 7, '/barometer': 8, '/GPS': 9, '/no_fault': 10}
    value = fault_type_dict[key]
    return value


def get_parse():
    # parse parameters
    parser = argparse.ArgumentParser(description='Dataset process tools')
    parser.add_argument('--original_path', type=str, default='./SampleData',
                        help='original data restore path')
    parser.add_argument('--restore_path', type=str, default='./ProcessData',
                        help='process data restore path')
    # sub-dataset:
    # default = 0, trans data in the SIL, HIL and Real folder
    # 1 for SIL, 2 for HIL, and 3 for Real
    # Note: if you only choose one sub-dataset type, please input as [X]
    parser.add_argument('--sub_dataset', type=int, nargs='+', default=[0],
                        choices=[0, 1, 2, 3],
                        help='select the sub_dataset you want')
    # fault type:
    # default = 0, trans all the fault type in the dataset
    # others occasions, please see readme.md
    # Note: if you only choose one sub-dataset type, please input as [X]
    parser.add_argument('--fault_type', type=int, nargs='+', default=[0],
                        choices=range(0, 12),
                        help='select the fault type you want')
    # flight status:
    # default = 0, trans all the flight type in the dataset
    # other occasions, please see readme.md
    # Note: if you only choose one sub-dataset type, please input as [X]
    parser.add_argument('--flight_status', type=int, nargs='+', default=[0],
                        choices=range(0, 7),
                        help='select the flight status you need')
    # trans num:
    # default = -1, trans all the flight cases in the dataset
    # if input other numbers, the program will change the transferred files.
    parser.add_argument('--trans_num', type=int, default=-1,
                        help='the number of cases to transfer')
    # trans frequency:
    # default = 20, users could change the frequency as they want
    parser.add_argument('--trans_freq', type=int, default=20,
                        help='the data frequency in processed files')
    return parser


if __name__ == "__main__":
    parser = get_parse() 

    args = parser.parse_args()
 
    print(args.flight_status, args.fault_type)