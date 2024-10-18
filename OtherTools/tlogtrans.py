import os
import shutil

class DataAllocator:
    def __init__(self, source_path, target_path):
        self.Data_source_path = source_path
        self.Data_target_path = target_path
        self.filelist = None
        
    def data_reader(self, labels):
        tlog_list = []
        csv_list = []
        for i in range(len(self.filelist)):
            return_num = self.check_labels(self.filelist[i], labels)
            if return_num == 1:
                tlog_list.append(self.filelist[i])
            elif return_num == 2:
                csv_list.append(self.filelist[i])
        print(tlog_list)
        print(csv_list)
        return tlog_list, csv_list

    def transfer_file(self, tlog_list, csv_list, mode=1):
        target_folder = os.listdir(self.Data_target_path)
        # target_folder = sorted(target_folder)
        print(target_folder)
        if mode == 2:
            length = len(target_folder)
            for i in range(length):
                tlog_path = self.Data_source_path + '//' + tlog_list[i]
                csv_path = self.Data_source_path + '//' + csv_list[i]
                target_tlog_path = self.Data_target_path + '//' + target_folder[i] + '//' + tlog_list[i]
                target_csv_path = self.Data_target_path + '//' + target_folder[i] + '//' + csv_list[i]
                shutil.move(tlog_path, target_tlog_path)
                shutil.move(csv_path, target_csv_path)
    
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
        if file_name[-5:] == labels[0]:
            return 1
        if file_name[-4:] == labels[1]:
            return 2
        return 0
    
    def Invert(self):
        target_folder = os.listdir(self.Data_target_path)
        length = len(target_folder)
        for i in range(length):
            files_list = os.listdir(self.Data_target_path + '//' + target_folder[i])
            for file in files_list:
                return_num = self.check_labels(file, ['.tlog', '.csv'])
                if return_num == 1 or return_num == 2:
                    file_path = self.Data_target_path + '//' + target_folder[i] + '//' + file
                    source_path = self.Data_source_path
                    shutil.move(file_path, source_path)


if __name__ == "__main__":
    # Only for tlog trans
    mode = 2
    source_file_path = 'F://CODE//python//Data_processing_tools//HIL_5//tlog'
    target_file_path = 'H://HIL_with_ROS_5'
    labels = ['.tlog', '.csv']
    DAcase = DataAllocator(source_file_path, target_file_path)
    DAcase.get_file_list()
    tlog_list, csv_list = DAcase.data_reader(labels)
    if mode == 1:
        print("Just Look!")
        DAcase.transfer_file(tlog_list, csv_list, mode=1)
    elif mode == 2:
        DAcase.transfer_file(tlog_list, csv_list, mode=2)
    elif mode == 3:
        DAcase.Invert()