from file_clean_up import *
import timeit

def test_auto_parse():
    a = RawData()
    file ="/Users/jimmyzhong/Desktop/seacliff_mot-04_20210526_summary.csv"
    print(timeit.timeit(lambda: a.auto_parse(file),number=1))
    assert 1 == 1
