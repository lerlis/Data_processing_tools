import csv


def file_reader(path):
    all_data = []
    with open(path, mode='r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        header_row = next(csvreader)
        all_data.append(header_row)
        for row in csvreader:
            all_data.append(row)
    return all_data


def data_check(data):
    header = data[0]
    row_length = len(header)
    filter_data = [header]
    filter_data.append(data[1])
    last_data = data[1]
    for i in range(2, len(data)):
        this_row_length = len(data[i])
        if this_row_length != row_length:
            print(data[i])
            continue
        elif abs(int(data[i][2]) - int(last_data[2])) > 5:
            print(data[i])
            continue
        else:
            filter_data.append(data[i])
            last_data = data[i]
    print('The origin length of data is: ', len(data))
    print('The filtered date length is: ', len(filter_data))
    return filter_data


def data_rewrite(data, name):
    with open(name, mode='w', encoding='utf-8', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)


if __name__ == "__main__":
    Data_path = 'F://CODE//Python//fault_data_process//_slash_mavros_slash_timesync_status.csv'
    all_data = file_reader(Data_path)
    filtered_data = data_check(all_data)
    data_rewrite(filtered_data, Data_path)
   