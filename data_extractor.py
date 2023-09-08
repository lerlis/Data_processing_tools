# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.
import json
import os

def get_keys(d, value):
    return [k for k, v in d.items() if v == value]

def data_dict_reader(file_path, key):
    with open(file_path, 'r', encoding='utf-8') as f:
        db_dict = json.load(f)
    # print(db_px4_dict['Real_PX4'])
    labels = []
    info_under_labels = []
    for k, v in db_dict.items():
        if type(v) is dict and k == key:
            for sk, sv in v.items():
                obtained_list = get_keys(sv, 1)
                if len(obtained_list) != 0:
                    labels.append(sk)
                    info_under_labels.append(obtained_list)
    return labels, info_under_labels

def data_extractor(selected_type):
    """
    selected_type = 1, for SIL;
    = 2, for HIL; and = 3, for real flight.
    """
    if selected_type == 1:  # For SIL
        labelp, infop = data_dict_reader('./data_SIL_PX4.json', 'SIL_PX4')
        label2, info2 = data_dict_reader('./data_SIL_GTD.json', 'SIL_Ground_Truth_Data')
    elif selected_type == 2:  # For HIL
        labelp, infop = data_dict_reader('./data_HIL_PX4.json', 'HIL_PX4')
        label2, info2 = data_dict_reader('./data_HIL_GTD.json', 'HIL_Ground_Truth_Data')
    elif selected_type == 3:  # For Real
        labelp, infop = data_dict_reader('./data_real_PX4.json', 'Real_PX4')
        label2, info2 = data_dict_reader('./data_real_ROS.json', 'Real_ROS')
    return labelp, infop, label2, info2


if __name__ == "__main__":
    data_extractor(3)