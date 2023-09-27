#!/usr/bin/python

# This file is used to fix bag files in ubuntu system.
# By using this file, all active bag files in this folder
# will be converted into normal state.


import os
import time

def orig_rename(name):
    process_temp = name.split('.')
    new_name = process_temp[0] + '.' + process_temp[1] + '.orig.' + process_temp[2]
    return new_name

def new_name(name):
    process_temp = name.split('.')
    new_name = process_temp[0] + '.' + process_temp[1]
    return new_name

listOfBagFiles = [f for f in os.listdir(".") if f[-7:] == ".active"]  # get list of only active bag files in current dir.
numberOfFiles = str(len(listOfBagFiles))
print ("reading all " + numberOfFiles + " active bagfiles in current directory: \n")

count = 0
for bagFile in listOfBagFiles:
    count += 1
    print("reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile)
    file_name = bagFile
    orig_file_name = orig_rename(file_name)
    new_file_name = new_name(file_name)
    print('Start reindex !!!!!')
    os.system('rosbag reindex {}'.format(file_name))
    time.sleep(10)
    print("Finished!!! Now start rosbag fix process!!")
    os.system("rosbag fix --force {} fix1.bag".format(file_name))
    # Decided by the file size of BAG, if the file is too large
    # the sleeping time maybe not enough
    time.sleep(60)  
    print("Finished!!!!")
    os.system('sudo rm -f {}'.format(file_name))
    os.system('sudo rm -f {}'.format(orig_file_name))
    time.sleep(10)
    os.system('mv fix1.bag {}'.format(new_file_name))