from file_clean_up import *
import timeit
import datetime as dt

def test_auto_parse():
    a = RawData()
    # a.settings = {'encode': 'utf-8', 'start_row': 2, 'end_row': -1, 'start_keyword': ' StartTime', 'end_keyword': ' EndTime', 'serial_number_keyword': 'UUT_Serial_Number', 'start_time_indicator': 'start', 'end_time_indicator': 'end', 'separator': ',', 'skip_keywords': [''], 'skip_rows': [''], 'col_name_set': None, 'sn_col': 'UUT_Serial_Number', 'start_time_col': ' StartTime', 'end_time_col': ' EndTime', 'start_col': 0, 'sn_col_candi': [], 'start_time_candi': [], 'end_time_candi': [], 'quotechar': '"'}
    file ="/Users/jimmyzhong/Desktop/seacliff_mot-04_20210526_summary.csv"
    a.settings.update({
        "timestamp_format": '%Y%m%d-%H%M%S',
        "start_row":3
    })
    print(timeit.timeit(lambda: a.auto_parse(file),number=1))

    # current_time = dt.datetime.now().timestamp()
    # time_str = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    # print(time_str)

    assert 1 == 1
