# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.

import numpy as np
import os
import time

from fileprocess import CSVFile_extractor
from timetrans import TimeBridgeofPX4andROS, TimeBridgeofPX4andGTD
from data_extractor import data_extractor
from get_parse import get_parse, parser_param_process, flight_id_dict, fault_id_dict

# The data frequency of processed data file.
# By use SET_FREQUENCY, the data will be unified into the same length
# SET_FREQUENCY = 20


def Real_data_reader(datapath, datatype, Set_frequency, restore_path):
    # 1 Find the data path, including PX4 data and ROS data
    CFEcase = CSVFile_extractor(datapath)
    PX4_file_folder, ROS_file_folder = CFEcase.folder_finder()
    # print(PX4_file_folder, ROS_file_folder)
    PX4_file_path = datapath + '\\' + PX4_file_folder
    # mode=1, re-generate based on conditions, mode=2, re-generate anyway
    _ = CFEcase.judge_ulog_trans(PX4_file_path, mode=1)
    # PX4_file_folder = 'log_0_2023-5-25-17-10-16'
    # ROS_file_folder = 'rfly_real_2023-05-25-17-09-00'
    # ********************************************************************************
    # 2 Extract key data and its timestamp,including:
    # (1)first arm and disarm time; (2)fly and land time;
    # (3)begin time of ROS and PX4, they are used to synchronize timestamp
    # file_name = PX4_file_folder + '_actuator_armed_0.csv'
    # labels = ['timestamp', 'armed', 'manual_lockdown', 'force_failsafe']
    # labels_format = ['int', 'int', 'int', 'int']
    # ArmData = CFEcase.DataFromCSV(file_name, labels, labels_format, PX4_file_folder)
    # ArmData = CFEcase.DataFromCSV_Panda(file_name, labels, PX4_file_folder)
    # ulogtime = CFEcase.get_start_end_time(ArmData)
    # print(ulogtime)

    # Use fly and land time as the begin and end of the processed data files
    file_name = PX4_file_folder + '_vehicle_land_detected_0.csv'
    labels = ['timestamp', 'ground_contact', 'has_low_throttle']
    LandData = CFEcase.DataFromCSV_Panda(file_name, labels, PX4_file_folder)
    flytime, landtime = CFEcase.find_fly_land_time(LandData)
    # print(flytime, landtime)

    # Find the begin time of Unix time and PX4 timestamp
    R_file_name = '_slash_mavros_slash_timesync_status.csv'
    R_labels = ['rosbagTimestamp', 'remote_timestamp_ns']
    # R_labels_format = ['int', 'int']
    # TimesyncData = CFEcase.DataFromCSV(R_file_name, R_labels, R_labels_format, ROS_file_folder)
    TimesyncData = CFEcase.DataFromCSV_Panda(R_file_name, R_labels, ROS_file_folder)
    start_time, end_time = TimesyncData[1], TimesyncData[-1]
    start_time_px4 = start_time[1] // 1000
    # print(start_time)
    # **********************************************************************************
    # 3 initialise timetools
    TimeTool = TimeBridgeofPX4andROS(ros_t=start_time[0], px4_t=start_time_px4)
    R_time_bias = TimeTool.CalculateTimebiasROS(end_time[0])
    end_time_px4 = TimeTool.ROStransPX4(R_time_bias)
    # Select the shortest time interval, and the generate target time
    new_fly_time = flytime if flytime > start_time_px4 else start_time_px4
    new_end_time = landtime if landtime < end_time_px4 else int(end_time_px4)
    # Set target timestamp by using SET_FREQUENCY
    target_timevec = range(new_fly_time, new_end_time,  int(1e6 * (1/Set_frequency)))
    new_time_seq = list(target_timevec)
    PX4_time_seq = np.array(new_time_seq)
    ROS_time_seq = CFEcase.PX4data_timestamp_trans(TimeTool, PX4_time_seq)
    data_index = np.array(list(range(0, len(PX4_time_seq), 1)))
    # **********************************************************************************
    # 4 Read data_dict from json, and then extract data
    labelp, infop, label2, info2 = data_extractor(datatype)
    all_data_head = []
    file_num = len(infop)
    for i in range(file_num):
        PX4_file_name = PX4_file_folder + labelp[i] + '.csv'
        info_read = ['timestamp'] + infop[i]
        data = CFEcase.DataFromCSV_Panda(PX4_file_name, info_read, PX4_file_folder)
        all_data_head.append(data[0])
        data = np.array(data[1:])
        new_data = CFEcase.freq_adjustment(data, target_timevec)
        # CFEcase.plot_data(new_time_seq, new_data[0])
        if i == 0:
            all_data = new_data
        else:
            all_data = np.concatenate((all_data, new_data), axis=1)
    file_num = len(info2)
    for i in range(file_num):
        ROS_file_name = label2[i] + '.csv'
        info_read = ['rosbagTimestamp'] + info2[i]
        data = CFEcase.DataFromCSV_Panda(ROS_file_name, info_read, ROS_file_folder)
        data = CFEcase.rosdata_timestamp_trans(TimeTool, data)
        all_data_head.append(data[0])
        data = np.array(data[1:])
        new_data = CFEcase.freq_adjustment(data, target_timevec)
        all_data = np.concatenate((all_data, new_data), axis=1)
    # Generate processed data header
    ros_name_list = CFEcase.Ros_file_name_simplify(label2)
    header = CFEcase.generate_data_header(labelp, ros_name_list, all_data_head)
    header = ['Index', 'Timestamp', 'rosbagTimestamp'] + header
    # timestamp concatenate
    all_data = np.concatenate((ROS_time_seq, all_data), axis=1)
    all_data = np.concatenate((np.array([PX4_time_seq]).T, all_data), axis=1)
    all_data = np.concatenate((np.array([data_index]).T, all_data), axis=1)
    all_data = np.concatenate(([header], all_data), axis=0)
    # Adjust RFLY_CTRL information and generate fault state in real flight
    all_data = CFEcase.RFLY_info_adjust(all_data)
    # Generate processed CSV files
    CFEcase.generate_CSV_data(all_data, restore_path)


def SHIL_data_reader(datapath, datatype, Set_frequency, restore_path):
    # 1 Find the data path, including PX4 data and Ground Truth data
    CFEcase = CSVFile_extractor(datapath)
    PX4_file_folder, GTD_file_folder = CFEcase.folder_finder_SH()
    # ********************************************************************************
    # 2 Extract key data and its timestamp,including:
    # (1)first arm and disarm time; (2)fly and land time;
    PX4_file_path = datapath + '\\' + PX4_file_folder
    # mode=1, re-generate based on conditions, mode=2, re-generate anyway
    ulg_name = CFEcase.judge_ulog_trans(PX4_file_path, mode=1)
    # file_name = ulg_name + '_actuator_armed_0.csv'
    # labels = ['timestamp', 'armed', 'manual_lockdown', 'force_failsafe']
    # ArmData = CFEcase.DataFromCSV_Panda(file_name, labels, PX4_file_folder)
    # ulogtime = CFEcase.get_start_end_time(ArmData)
    # Use fly and land time as the begin and end of the processed data files
    file_name = ulg_name + '_vehicle_land_detected_0.csv'
    labels = ['timestamp', 'ground_contact', 'has_low_throttle']
    LandData = CFEcase.DataFromCSV_Panda(file_name, labels, PX4_file_folder)
    flytime, landtime = CFEcase.find_fly_land_time(LandData)
    # print(flytime, landtime)
    # Find the begin time of PX4 timestamp in GTD
    G_file_name = 'UAVState_data.xlsx'
    G_labels = ['uavTime']
    CFEcase.ConvertXLSXtoCSV(G_file_name, GTD_file_folder)
    G_file_name = 'UAVState_data.csv'
    TimeData = CFEcase.DataFromCSV_Panda(G_file_name, G_labels, GTD_file_folder)
    # print(TimeData)
    start_time, end_time = TimeData[1]*1000, TimeData[-1]*1000
    # print(start_time, end_time)
    G_file_name = 'TrueState_data.xlsx'
    G_labels = ['trueTime']
    CFEcase.ConvertXLSXtoCSV(G_file_name, GTD_file_folder)
    G_file_name = 'TrueState_data.csv'
    TimeData = CFEcase.DataFromCSV_Panda(G_file_name, G_labels, GTD_file_folder)
    T_start_time, T_end_time = TimeData[1], TimeData[-1]
    # print(T_start_time, T_end_time)
    # **********************************************************************************
    # 3 initialise timestamp tools
    TimeTool = TimeBridgeofPX4andGTD(gtd_t=T_start_time, px4_t=start_time)

    T_start_time_bias = TimeTool.CalculateTimebiasGTD(T_start_time)
    T_start_time = int(TimeTool.GTDtransPX4(T_start_time_bias))
    T_end_time_bias = TimeTool.CalculateTimebiasGTD(T_end_time)
    T_end_time = int(TimeTool.GTDtransPX4(T_end_time_bias))
    # print(T_start_time, T_end_time)
    # Select the shortest time interval
    new_fly_time = flytime if flytime > start_time else start_time
    new_end_time = end_time if end_time < landtime else landtime
    new_end_time = new_end_time if new_end_time < T_end_time else T_end_time
    # Generate target time vector
    target_timevec = range(new_fly_time, new_end_time,  int(1e6 * (1/Set_frequency)))
    target_timevec_ms = range(new_fly_time//1000, new_end_time//1000,  int(1e3 * (1/Set_frequency)))
    
    new_fly_time_bias = TimeTool.CalculateTimebiasPX4(new_fly_time)
    GTD_fly_time = TimeTool.PX4transGTD(new_fly_time_bias)
    new_end_time_bias = TimeTool.CalculateTimebiasPX4(new_end_time)
    GTD_end_time = TimeTool.PX4transGTD(new_end_time_bias)
    # print(GTD_fly_time, GTD_end_time)
    
    target_timevec_s = np.arange(GTD_fly_time, GTD_end_time, 1/Set_frequency)
    # print(target_timevec_s)

    new_time_seq = list(target_timevec)
    PX4_time_seq = np.array(new_time_seq)
    GTD_time_seq = np.array(list(target_timevec_s))
    data_index = np.array(list(range(0, len(PX4_time_seq), 1)))
    # print(len(PX4_time_seq), len(GTD_time_seq), len(data_index))
    # **********************************************************************************
    # 4 Read data_dict from json, and then extract data
    labelp, infop, label2, info2 = data_extractor(datatype)
    all_data_head = []
    for i in range(len(infop)):
        PX4_file_name = ulg_name + labelp[i] + '.csv'
        info_read = ['timestamp'] + infop[i]
        data = CFEcase.DataFromCSV_Panda(PX4_file_name, info_read, PX4_file_folder)
        all_data_head.append(data[0])
        data = np.array(data[1:])
        new_data = CFEcase.freq_adjustment(data, target_timevec)
        if i == 0:
            all_data = new_data
        else:
            all_data = np.concatenate((all_data, new_data), axis=1)
    for i in range(len(info2)):
        GTD_file_name = label2[i] + '.csv'
        if GTD_file_name[:4] == 'True':
            info_read = ['trueTime'] + info2[i]
        elif GTD_file_name[:4] == 'UAVS':
            info_read = ['uavTime'] + info2[i]
        data = CFEcase.DataFromCSV_Panda(GTD_file_name, info_read, GTD_file_folder)
        all_data_head.append(data[0])
        data = np.array(data[1:])
        if GTD_file_name[:4] == 'True':
            new_data = CFEcase.freq_adjustment(data, target_timevec_s)
        elif GTD_file_name[:4] == 'UAVS':
            new_data = CFEcase.freq_adjustment(data, target_timevec_ms)
        all_data = np.concatenate((all_data, new_data), axis=1)
    # Generate processed data header
    header = CFEcase.generate_data_header(labelp, label2, all_data_head)
    header = ['Index', 'Timestamp', 'trueTime'] + header
    # timestamp concatenate
    all_data = np.concatenate((np.array([GTD_time_seq]).T, all_data), axis=1)
    all_data = np.concatenate((np.array([PX4_time_seq]).T, all_data), axis=1)
    all_data = np.concatenate((np.array([data_index]).T, all_data), axis=1)
    all_data = np.concatenate(([header], all_data), axis=0)
    # Adjust RFLY_CTRL information and generate fault state in real flight
    all_data = CFEcase.RFLY_info_adjust(all_data)
    CFEcase.generate_CSV_data(all_data, restore_path)


def CaseID_generator(data_type, flight_mode, fault_type, case_num):
    caseID = data_type * 1000000000 + flight_mode * 100000000 + fault_type * 1000000 + case_num
    return caseID


if __name__ == "__main__":
    parser = get_parse()
    params = parser.parse_args()
    original_path, restore_path, sub_dataset_path, flight_status_path, fault_type_path, trans_num, Set_frequency = parser_param_process(params)
    print(original_path)
    print(restore_path)
    print(sub_dataset_path)
    print(flight_status_path)
    print(fault_type_path)
    print(trans_num)
    print(Set_frequency)
    START_TIME = time.time()
    for i in range(len(sub_dataset_path)):
        if sub_dataset_path[i] == '/SIL':
            DataType = 1
        elif sub_dataset_path[i] == '/HIL':
            DataType = 2
        elif sub_dataset_path[i] == '/Real':
            DataType = 3
        for j in range(len(flight_status_path)):
            for k in range(len(fault_type_path)):
                # structure path
                structure_path = original_path + sub_dataset_path[i] + flight_status_path[j] + fault_type_path[k]
                if os.path.exists(structure_path):
                    dir_list = os.listdir(structure_path)
                    # print(dir_list)
                    case_number = len(dir_list)
                    if case_number != 0:
                        if trans_num == -1:
                            pass  # Default, transfer all the data case in structure path
                        else:
                            case_number = min(trans_num, case_number)
                        for l in range(case_number):
                            caseID = CaseID_generator(DataType, flight_id_dict(flight_status_path[j]), fault_id_dict(fault_type_path[k]), l)
                            Restore_path = restore_path + '/Case_{}.csv'.format(caseID)
                            data_path = structure_path + '/' + dir_list[l]
                            if DataType == 3:
                                print(data_path)
                                Real_data_reader(data_path, DataType, Set_frequency, Restore_path)
                                print(time.time() - START_TIME)
                            elif DataType == 2 or DataType == 1:
                                SHIL_data_reader(data_path, DataType, Set_frequency, Restore_path)
                                print(time.time() - START_TIME)
                else:
                    print('This path: ', structure_path, 'doesn\'t exist!')
                    print('Please check again!!')

    """
    DataType = 1, for SIL;
    = 2, for HIL; and = 3, for real flight.
    """
    # DataType = 3
    # DataPath = 'F:\\CODE\\Python\\fault_data_process\\SampleData\\Real\\hover\\56_1'
    # Real_data_reader(DataPath, DataType)
    # DataType = 1
    # DataPath = 'F:\\CODE\\Python\\fault_data_process\\SampleData\\SIL\\hover\\TestCase_4_1002000003'
    # SHIL_data_reader(DataPath, DataType)
