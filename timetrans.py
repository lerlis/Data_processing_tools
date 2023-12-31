# -*- coding: utf-8 -*-
# Copyright (C) rflylab from School of Automation Science and Electrical Engineering, Beihang University.
# All Rights Reserved.
import time
import numpy as np


class TimeBridgeofPX4andROS:
    def __init__(self, ros_t, px4_t):
        self.ROS_start_time = ros_t
        self.PX4_start_time = px4_t

    def RosTimeStamp2Date(self, rostimestamp):
        # RosTimeStamp is Unix time
        # timestamp = 1684207343587960000 (Example)
        timestamp = rostimestamp
        secs = int(np.round(timestamp / 1e9))
        s_l = time.localtime(secs)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", s_l)
        # print(ts)
        return ts

    def Date2RosTimeStamp(self, date):
        # t = '2015-01-01 00:00:00'
        t = date
        s_t = time.strptime(t, "%Y-%m-%d %H:%M:%S")
        mkt = int(time.mktime(s_t))
        # print(mkt)
        return mkt

    def CalculateTimebiasROS(self, now_ROS_timestamp):
        Timebias = now_ROS_timestamp - self.ROS_start_time
        # Units below: seconds (s)
        Timebias = round((Timebias / 1e9), 6)
        return Timebias

    def CalculateTimebiasPX4(self, now_PX4_timestamp):
        Timebias = now_PX4_timestamp - self.PX4_start_time
        # Units below: seconds (s)
        Timebias = round((Timebias / 1e6), 6)
        return Timebias
    
    def PX4transROS(self, timebias):
        ROS_timestamp = self.ROS_start_time + timebias * 1e9
        return ROS_timestamp

    def ROStransPX4(self, timebias):
        PX4_timestamp = self.PX4_start_time + timebias * 1e6
        return PX4_timestamp


class TimeBridgeofPX4andGTD:
    def __init__(self, gtd_t, px4_t):
        self.GTD_start_time = gtd_t
        self.PX4_start_time = px4_t

    def CalculateTimebiasGTD(self, now_GTD_timestamp):
        # Units below: seconds (s)
        Timebias = now_GTD_timestamp - self.GTD_start_time
        return Timebias
    
    def CalculateTimebiasPX4(self, now_PX4_timestamp):
        Timebias = now_PX4_timestamp - self.PX4_start_time
        # Units below: seconds (s)
        Timebias = round((Timebias / 1e6), 6)
        return Timebias

    def PX4transGTD(self, timebias):
        GTD_timestamp = self.GTD_start_time + timebias
        return GTD_timestamp

    def GTDtransPX4(self, timebias):
        PX4_timestamp = self.PX4_start_time + timebias * 1e6
        return PX4_timestamp


if __name__ == "__main__":
    Timebias = 1684207343587960000
    Timebias = round((Timebias / 1e9), 3)
    print(Timebias)