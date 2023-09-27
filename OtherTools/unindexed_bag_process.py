import time
import os #for file management make directory

# This file realize the same function in 'bag_active_process.py'
# The difference is that all function are integrated in one CLASS,
# and could be called by other programs.

class unindexed_processor:
    def __init__(self, name):
        self.processor_path = os.path.dirname(__file__)
        self.file_name = name
        self.orig_file_name = self.orig_rename(self.file_name)
    
    def reindexandfix(self):
        os.chdir(self.processor_path)
        # print(self.processor_path)
        print('Start reindex !!!!!')
        os.system('rosbag reindex {}'.format(self.file_name))
        time.sleep(10)
        print("Finished!!! Now start rosbag fix process!!")
        os.system("rosbag fix --force {} fix1.bag".format(self.file_name))
        time.sleep(60)
        print("Finished!!!!")
        os.system('sudo rm -f {}'.format(self.file_name))
        os.system('sudo rm -f {}'.format(self.orig_file_name))
        time.sleep(10)
        os.system('mv fix1.bag {}'.format(self.file_name))

    def orig_rename(self, name):
        process_temp = name.split('.')
        new_name = process_temp[0] + '.orig.' + process_temp[1]
        return new_name


