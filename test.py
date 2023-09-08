import openpyxl
import os
import numpy as np

# name  = 'log_6_2023-5-17-15-43-36_actuator_armed_0.csv'

# lst = name.split(".")
# print(lst)
# llst = lst[0].split("_")
# print(llst)
# llst = llst[3:]
# print(llst)
# new_name = ''
# for i in range(len(llst)):
#     new_name = new_name + '_' + llst[i]

# print(new_name)

# path = 'H:\\SampleData\\HIL\\acce\\TestCase_1_2400000000\\TrueData\\TrueState_data.xlsx'
# wb = openpyxl.load_workbook(path)
# sheet = wb.worksheets[0]
# header = []
# for row in sheet[1]:
#     header.append(row.value)

# print(header)

a = np.array([[1,2,3],
              [4,5,6]])

a = '_slash_mavros_slash_offb_flight_mode_slash_send_data'
index = a.find('_slash_mavros_slash_')
print(index)

