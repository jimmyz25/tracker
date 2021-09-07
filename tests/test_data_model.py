import datetime
from unittest import TestCase

from data_model import *
import random
import string
import pandas as pd

db = DBsqlite(RMD)
gold = DBsqlite(golden)


# db.__connect__()
#
# #
# for i in range (30000):
#     a = random.randint(1,40)
#     b = ''.join(random.choices(string.ascii_uppercase +
#         string.digits, k=12))
#     cc = datetime.timedelta(minutes=random.randrange(100000))+datetime.datetime(2021,2,1,12,00)
#     c = cc.timestamp()
#     d = random.randint(50000, 10000000)
#     e = random.randint(1,50)
#     k = random.choice(["station1","station2","lab","tester1"])
#     x = dt.datetime.strftime(cc,"%Y-%m-%d %I:%M:%S %p")
#     db.cur.execute("INSERT INTO Config_SN_T (Config_FK,SerialNumber, DateAdded, WIP,Stress_FK) Values (?,?,?,?,?)",(a,b,c,d,e))
#     db.cur.execute("INSERT INTO RelLog_T (Station,SerialNumber, StartTimestamp, WIP,FK_RelStress,StartTime) Values (?,?,?,?,?,?)",(k,b,c,d,e,x))
#     db.con.commit()
# db.con.close()


def test_sn_exist():
    print(timeit.timeit(lambda: db.sn_exist("32ANN3Q31MRB"), number=1000))
    for i in range(1):
        assert db.sn_exist("32ANN3Q31MRB") is True


def test_stress_exist():
    print(timeit.timeit(lambda: db.stress_exist(1), number=1000))
    assert 1 == 1


def test_sync_sn_table():
    gold.sync_sn_table(db.cache_sn_table)
    db.sync_sn_table(gold.cache_sn_table)
    assert True is True


def test_sync_wip_table():
    gold.sync_wip_table(db.cache_wip_table)
    db.sync_wip_table(gold.cache_wip_table)
    assert True is True


def test_wip_exist():
    print(timeit.timeit(lambda: db.wip_exist(("asdfasdf")), number=1000))
    assert db.wip_exist("assdf") is False


def test_config_exist():
    print(timeit.timeit(lambda: db.config_exist(1), number=1000))
    assert db.config_exist(1) is True


#
# def test_key_filter():
#     def func(x):
#         return x.get("SerialNumber") == "32ANN3Q31MRB"
#
#     for i in range(1):
#         a = db.cache_sn_table.key_filter("32ANN3Q31MRB").record_filter(func)
#         print(timeit.timeit(lambda: db.cache_sn_table.key_filter("32ANN3Q31MRB").record_filter(func), number=1000))
#         assert a.records.get("32ANN3Q31MRB").get("Config_FK") == 13


def test_sync_config_table():
    for i in range(1):
        db.sync_config_table(gold.cache_config_table)
    assert 1 == 1


def test_sync_stress_table():
    for i in range(10):
        db.sync_stress_table(gold.cache_stress_table)
    assert 1 == 1


def test_rel_stress():
    stress = StressModel(1, db)
    assert stress.rel_stress == "RelStress1"


def test_rel_checkpoint():
    stress = StressModel(1, db)
    assert stress.rel_checkpoint == "RelCheckpoint1-1"


def test_SN_init():
    sn = SnModel("41C36MX9YSJM", db)
    print(timeit.timeit(lambda: SnModel("41C36MX9YSJM", db), number=1000))
    assert sn.config.config_name == "Config11"
    assert sn.config.program == "Program1"


#
# def test_latest_sn_history():
#     for i in range(1):
#         a = db.cache_latest_sn_history
#         # delattr(db,"cache_latest_sn_history")
#         assert a.records.get("41C36MX9YSJM").get("Config_FK") == 1


def test_selected_config_pks():
    db.filter_set.update({"program": "Program1"})
    db.filter_set.update({"build": "P1"})
    db.filter_set.update({"config": "Config11"})
    print(timeit.timeit(lambda: db.selected_config_pks, number=1000))
    a = db.selected_config_pks
    assert a.pop() == 1


def test_config_list_to_select():
    db.filter_set.update({"program": "Program1"})
    db.filter_set.update({"build": "P1"})
    a = db.config_list_to_select
    assert a == {"Config11", "Config12", "Config13"}


def test_ckp_list_to_select():
    db.filter_set.update({"stress": "HTHH(6590)"})
    a = db.ckp_list_to_select
    assert a == {"HTHH72hr", "HTHH144hr", "HTHH256hr"}


def test_selected_ckp_pks():
    db.filter_set.clear()
    db.filter_set.update({"stress": "RelStress1"})
    db.filter_set.update({"checkpoint": "RelCheckpoint1-1"})
    a = db.selected_stress_pks
    assert a.pop() == 1


def test_filtered_record():
    db.filter_set.clear()
    db.filter_set.update({"serial_number": "41C36MX9YSJM"})
    db.filter_set.update({"wip": "1675676"})
    db.filter_set.update({"filter_table": "RelLog_T"})
    print(timeit.timeit(lambda: db.filtered_record, number=1000))
    a = db.filtered_record
    assert a[0]["SerialNumber"] == "41C36MX9YSJM"


# def test_record_filter():
#     def func(x):
#         return x.get("SerialNumber") in {"32ANN3Q31MRB", "dfasdf"}
#
#     db.filter_set.update({"filter_table": "RelLog_T"})
#     # a = db.cache_sn_table.record_filter(func=func).record_filter(func=func)
#     a = db.
#     print(timeit.timeit(lambda: db.cache_sn_table.record_filter(func=func).record_filter(func=func), number=100))
#     assert a.records.get("32ANN3Q31MRB").get("Config_FK") == 13

#
# def test_dbsqlite():
#     db.__connect__()
#     print(timeit.timeit(lambda: db.con.backup(db.db_memory), number=20))
#     # for i in range (100):
#     #     a = db.__db_create_latest_sn_history__()
#     assert 1 == 1


def test_sql_filter_str():
    kwp = {
        "CONFIG_FK": (1, 2, 3),
        "SerialNumber": "abc",
        "Program": "program1"
    }

    print(db.sql_filter_str(kwp))
    assert 1 == 1


def test_program_list():
    a = db.program_list
    print(a)
    print(timeit.timeit(lambda: db.program_list, number=1000))
    assert a == {'Program1', 'Program2'}


def test_stress_list():
    a = db.stress_list
    print(a)
    print(timeit.timeit(lambda: db.stress_list, number=1000))
    assert a == {'HTHH(6590)', 'RelStress1'}


def test_sync_rel_log_table():
    gold.sync_rel_log_table(db.cache_rel_log_table)
    assert True == True
