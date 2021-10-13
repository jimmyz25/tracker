from file_clean_up import *
import timeit
from data_model import *
import datetime as dt

RMD = "/Users/jimmyzhong/Desktop/Empty DB for Training.db"
db = DBsqlite(RMD)
golden_address = "/Users/mingyuzhong/Documents/tracker/ReliabilityManagementDB copy.db"
gold = DBsqlite(golden_address)


def test_auto_parse():
    a = RawData()
    # a.settings = {'encode': 'utf-8', 'start_row': 2, 'end_row': -1, 'start_keyword': ' StartTime', 'end_keyword': ' EndTime', 'serial_number_keyword': 'UUT_Serial_Number', 'start_time_indicator': 'start', 'end_time_indicator': 'end', 'separator': ',', 'skip_keywords': [''], 'skip_rows': [''], 'col_name_set': None, 'sn_col': 'UUT_Serial_Number', 'start_time_col': ' StartTime', 'end_time_col': ' EndTime', 'start_col': 0, 'sn_col_candi': [], 'start_time_candi': [], 'end_time_candi': [], 'quotechar': '"'}
    file = "/Users/jimmyzhong/Desktop/seacliff_mot-04_20210526_summary.csv"
    a.settings.update({
        "timestamp_format": '%Y%m%d-%H%M%S',
    })
    # print(timeit.timeit(lambda: a.auto_parse(file), number=1))
    result = a.auto_parse(file)
    print(result)
    # rel_tag = [db.rel_tagging(a[1], a[0]) for a in result[1:]]
    # print (rel_tag)

    # current_time = dt.datetime.now().timestamp()
    # time_str = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    # print(time_str)

    assert 1 == 1


def test_search_match_in_files():
    assert False


def test_clean_up_file():
    a = RawData()
    a.settings.update(
        {
            "separator": ",",
        }
    )
    file = '/Users/jimmyzhong/Desktop/5385BZ_VID-1_Summary_20210526_G25TC_P_R_MPK.csv'
    result = a.clean_up_file(file)
    print(result)
    assert 1 == 1


def test_concat_matching_files():
    """
    bring starttime and serialnumber to first, all text column to front, all numbers to back
    :return:
    """
    a = RawData()
    a.settings.update(
        {
            "separator": ",",
            "start_time_col": "Start Time",
            "timestamp_format": "%Y/%m/%d %H:%M:%S",
            "sn_col": "Lens Housing Barcode"
        }
    )
    file_list = ['/Users/jimmyzhong/Desktop/5385BZ_VID-1_Summary_20210526_G25TC_P_R_MPK.csv',
            '/Users/jimmyzhong/Desktop/5385BZ_VID-1_Summary_20210526_G25TC_P_R_MPK.csv']
    result = a.concat_matching_files(file_list,db)
    assert 1 == 1
