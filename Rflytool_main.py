# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.

import numpy as np

from fileprocess import CSVFile_extractor
from timetrans import TimeBridgeofPX4andROS
from data_extractor import data_extractor

# The data frequency of processed data file.
# By use SET_FREQUENCY, the data will be unified into the same length
SET_FREQUENCY = 20


def Real_data_reader(datapath, datatype):
    # 1 Find the data path, including PX4 data and ROS data
    CFEcase = CSVFile_extractor(datapath)
    PX4_file_folder, ROS_file_folder = CFEcase.folder_finder()
    # print(PX4_file_folder, ROS_file_folder)
    # PX4_file_folder = 'log_0_2023-5-25-17-10-16'
    # ROS_file_folder = 'rfly_real_2023-05-25-17-09-00'
    # ********************************************************************************
    # 2 Extract key data and its timestamp,including:
    # (1)first arm and disarm time; (2)fly and land time;
    # (3)begin time of ROS and PX4, they are used to synchronize timestamp
    file_name = PX4_file_folder + '_actuator_armed_0.csv'
    labels = ['timestamp', 'armed', 'manual_lockdown', 'force_failsafe']
    # labels_format = ['int', 'int', 'int', 'int']
    # ArmData = CFEcase.DataFromCSV(file_name, labels, labels_format, PX4_file_folder)
    ArmData = CFEcase.DataFromCSV_Panda(file_name, labels, PX4_file_folder)
    ulogtime = CFEcase.get_start_end_time(ArmData)
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
    start_time = TimesyncData[1]
    # print(start_time)
    # **********************************************************************************
    # 3 initialise timetools
    TimeTool = TimeBridgeofPX4andROS(ros_t=start_time[0], px4_t=start_time[1]//1000)
    # Set target timestamp by using SET_FREQUENCY
    target_timevec = range(flytime, landtime,  int(1e6 * (1/SET_FREQUENCY)))
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
    # Generate processed CSV files
    CFEcase.generate_CSV_data(all_data, 'processed_files.csv')


if __name__ == "__main__":
    """
    DataType = 1, for SIL;
    = 2, for HIL; and = 3, for real flight.
    """
    DataType = 3
    DataPath = 'F:\\CODE\\Python\\fault_data_process\\SampleData\\Real\\hover\\56_1'
    Real_data_reader(DataPath, DataType)