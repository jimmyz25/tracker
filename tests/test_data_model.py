# import datetime
# from unittest import TestCase
import timeit
from data_model import *
# import random
# import string
# import pandas as pd

RMD = "/Users/jimmyzhong/Desktop/Tracker App package/Demo Package/RelStationDB.db"
db = DBsqlite(RMD)
golden_address = "/Users/mingyuzhong/Documents/tracker/ReliabilityManagementDB copy.db"
gold = DBsqlite(golden_address)


def test_sn_exist():
    print(timeit.timeit(lambda: db.sn_exist("32ANN3Q31MRB"), number=1000))
    for i in range(1):
        assert db.sn_exist("AA") is False


def test_stress_exist():
    print(timeit.timeit(lambda: db.stress_exist(1), number=1000))
    assert 1 == 1


# def test_sync_sn_table():
#     gold.sync_sn_table(db.cache_sn_table)
#     db.sync_sn_table(gold.cache_sn_table)
#     assert True is True
#
#
# def test_sync_wip_table():
#     gold.sync_wip_table(db.cache_wip_table)
#     db.sync_wip_table(gold.cache_wip_table)
#     assert True is True


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


# def test_sync_config_table():
#     db.sync_config_table(gold.cache_config_table)
#     assert 1 == 1
#
#
# def test_sync_stress_table():
#     db.sync_stress_table(gold.cache_stress_table)
#     assert 1 == 1


def test_rel_stress():
    stress = StressModel(1, db)
    assert stress.rel_stress == "RelStress1"


def test_rel_checkpoint():
    stress = StressModel(1, db)
    assert stress.rel_checkpoint == "RelCheckpoint1-1"


def test_SN_init():
    sn = SnModel("AA", db)
    print(timeit.timeit(lambda: SnModel("AA", db), number=1000))
    assert sn.config.config_name == "Config13"
    assert sn.config.program == "Program1"


#
# def test_latest_sn_history():
#     for i in range(1):
#         a = db.cache_latest_sn_history
#         # delattr(db,"cache_latest_sn_history")
#         assert a.records.get("41C36MX9YSJM").get("Config_FK") == 1


def test_selected_config_pks():
    db.filter_set.clear()
    db.filter_set.update({"program": "Program1"})
    # db.filter_set.update({"build": "P1"})
    # db.filter_set.update({"config": "Config11"})
    # print(timeit.timeit(lambda: db.selected_config_pks, number=1000))
    print(db.selected_config_pks)
    a = db.selected_config_pks
    assert a == {"1", "2", "3"}


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
    assert a.pop() == "1"


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
        'PK': [3],
        "CONFIG_FK": "sd",
        "SerialNumber": None,
        "Program": {1, 2, 3, 4}
    }
    print(db.sql_filter_str(kwp))
    # print(db.sql_filter_str(kwp))
    # kwp = {'RelLog_T.WIP': None, 'RelLog_T.SerialNumber': None, 'Config_FK': {1, 2, 3, 4},
    #        'FK_RelStress': {1, 10, 20, 21}}
    #
    # # print(db.sql_filter_str(kwp))
    # db.filter_set.clear()
    # db.filter_set.update({'program': 'Program1', 'build': 'P1', 'config': 'Config13'})

    assert 1 == 1


def test_program_list():
    a = db.program_list
    print(a)
    print(timeit.timeit(lambda: db.program_list, number=1000))
    assert a == {'Program1', 'Program2'}


def test_stress_list():
    a = db.stress_list
    print(timeit.timeit(lambda: db.stress_list, number=1000))
    assert a == {'HTHH(6590)', 'RelStress1'}


def test_sync_rel_log_table():
    db.sync_rel_log_table(golden_address, station="RelStation#1")
    assert True == True


def test_latest_sn_history():
    db.filter_set.clear()
    db.filter_set.update({"serial_number": "41C36MX9YSJM"})
    db.filter_set.update({"wip": "1675676"})
    db.filter_set.update({"filter_table": "RelLog_T"})
    print(timeit.timeit(lambda: db.latest_sn_history, number=1000))

    assert 1 == 1


def test_unit_count():
    count = ConfigModel(1, db).unit_count
    print(timeit.timeit(lambda: ConfigModel(1, db).unit_count, number=1000))
    assert count == 0


def test_rel_log_table_view_data():
    db.filter_set.clear()
    # db.filter_set.update({"serial_number": "41C36MX9YSJM"})
    # db.filter_set.update({"wip": "1675676"})
    # db.filter_set.update({"filter_table": "RelLog_T"})
    print(timeit.timeit(lambda: db.rel_log_table_view_data, number=1))
    a = db.rel_log_table_view_data
    assert True == True


def test_ready_to_checkin():
    db.filter_set.update({"selected_pks": [1, 2, 1]})
    print(timeit.timeit(lambda: db.ready_to_checkin, number=1))
    assert db.ready_to_checkin == False


def test_ready_to_checkout():
    db.filter_set.update({"selected_pks": ["aa"]})
    print(timeit.timeit(lambda: db.ready_to_checkout, number=1))
    assert db.ready_to_checkin == False


def test_ready_to_add():
    db.filter_set.update({"serial_number_list": "66T6S8L9M76P, 41C36MX9YSJM, \n F6EZDQRQOSMP "})
    print(db.ready_to_add)
    print(db.filter_set)
    assert True == True


def test_fa_log_table_view_data():
    db.filter_set.clear()
    # db.filter_set.update({"serial_number": "41C36MX9YSJM"})
    # db.filter_set.update({"wip": "1675676"})
    # db.filter_set.update({"filter_table": "RelLog_T"})
    print(timeit.timeit(lambda: db.fa_log_table_view_data, number=1))
    a = db.fa_log_table_view_data
    assert True == True


def test_failure_mode_group_list():
    # db.failure_mode_group_list
    print(timeit.timeit(lambda: db.failure_mode_group_list, number=1000))
    print(db.failure_mode_group_list)
    assert True == True


def test_failure_mode_list_to_select():
    db.filter_set.clear()
    db.filter_set.update({"failure_group": "Default"})
    print(timeit.timeit(lambda: db.failure_mode_list_to_add_to_sn, number=1000))
    print(db.failure_mode_list_to_add_to_sn)
    assert True == True


# def test_get_total_in_cell_display():
#     a = status_summary(db)
#     b = a.get_total_in_cell_display("90e52e7a-20e6-11ec-a422-1e00d9211e69", "94695890-20e7-11ec-ba51-1e00d9211e69")
#     assert True == True

#
# def test_tree_to_display():
#     a = status_summary(db)
#     b = a.tree_to_display()
#     assert True == True


def test_get_test_history():
    history = db.get_test_history(sn="03734D43H7")
    print(history)
    assert True == True


def test_rel_tagging():
    rel_tag = db.rel_tagging(sn="03734D43H7", timestamp=1633639328)
    print(rel_tag)
    rel_tag = db.rel_tagging(sn="03734D43H7", timestamp=1633639353)
    print(rel_tag)
    rel_tag = db.rel_tagging(sn="03734D43H7", timestamp=1633639392)
    print(rel_tag)
    rel_tag = db.rel_tagging(sn="03734D43H7", timestamp=1633639394)
    print(rel_tag)
    assert True == True


def test_weibull_output():
    db.filter_set.update({
        "failure_mode": "Display Crack"
    })
    sn = "06QGLA3FX"
    failureMode = "Lens detach"
    a = db.weibull_output(sn)
    print(a)

    assert 1 == 1
