from file_clean_up import *


def test_auto_parse():
    a = RawData()
    file ="/Users/jimmyzhong/Desktop/seacliff_mot-04_20210526_summary.csv"
    a.auto_parse(file)
    assert 1 == 1
