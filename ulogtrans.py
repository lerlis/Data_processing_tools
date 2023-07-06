import os
import shutil

class UlogProcessor:
    def __init__(self, input_path):
        self.ProcessorPath = os.path.dirname(__file__)
        self.DataPath = input_path

    def Create_folder(self, name):
        self.TargetFilder_log = self.DataPath + '/' + name
        if os.path.exists(self.TargetFilder_log):  # 如果有同名的文件夹，则删除重建
            shutil.rmtree(self.TargetFilder_log)
        os.makedirs(self.TargetFilder_log)

    def Ulog2csv_py(self):
        dirs = os.listdir(self.DataPath)
        print(dirs)
        ulog_dirs = []
        ulog_name = []
        for dir in dirs:
            process_temp = dir.split('.')
            # print(process_temp)
            if len(process_temp) == 2 and process_temp[1] == 'ulg':
                ulog_dirs.append(dir)
                ulog_name.append(process_temp[0])
        print(ulog_dirs)
        for i in range(len(ulog_dirs)):
            self.Create_folder(ulog_name[i])
            path = os.path.join(self.DataPath, ulog_dirs[i])
            TargetPath_log = self.TargetFilder_log + '/{}'.format(ulog_dirs[i])
            shutil.copyfile(path, TargetPath_log)
            os.chdir(self.TargetFilder_log)
            os.system("for %i in (*); do ulog2csv %i")
            os.chdir(self.DataPath)
        print('Finished ALL!!!')


if __name__ == "__main__":
    path = 'F://健康评估//数据集论文//实飞//怀来实飞数据//680//0616'
    UPcase = UlogProcessor(path)
    UPcase.Ulog2csv_py()

