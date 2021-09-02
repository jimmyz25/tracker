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

def test_clear_cache():
    db.clear_cache("adf")
    assert 1 == 1


def test_sn_exist():
    db = DBsqlite(RMD)
    for i in range(100):
        assert db.sn_exist("a") is False


def test_update_sn_table():
    gold.sync_sn_table(db.cache_sn_table)
    db.sync_sn_table(gold.cache_sn_table)
    assert True is True


def test_sync_wip_table():
    gold.sync_wip_table(db.cache_wip_table)
    db.sync_wip_table(gold.cache_wip_table)
    assert True is True


def test_wip_exist():
    assert db.wip_exist("assdf") is False


def test_config_exist():
    assert db.config_exist(100) is False


def test_record_filter():
    def func(x):
        return x.get("SerialNumber") in {"32ANN3Q31MRB", "dfasdf"}

    for i in range(100):
        a = db.cache_sn_table.record_filter(func=func).record_filter(func=func)
    assert a.records.get("32ANN3Q31MRB").get("Config_FK") == 13


def test_key_filter():
    def func(x):
        return x.get("SerialNumber") == "32ANN3Q31MRB"

    for i in range(100):
        a = db.cache_sn_table.key_filter("32ANN3Q31MRB").record_filter(func)
        assert a.records.get("32ANN3Q31MRB").get("Config_FK") == 13


def test_sync_config_table():
    for i in range(10):
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


def test_stress():
    for i in range(10):
        sn = SnModel("41C36MX9YSJM", db)
        assert sn.config.config_name == "Config11"
        assert sn.config.program == "Program1"


def test_latest_sn_history():
    a = db.cache_latest_sn_history
    for i in range(1):
        assert a.records.get("41C36MX9YSJM").get("Config_FK") == 1


def test_selected_config_pk():
    db.filter_set.update({"program": "Program1"})
    db.filter_set.update({"build": "P1"})
    db.filter_set.update({"config": "Config11"})
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
    db.filter_set.update({"stress": "RelStress1"})
    db.filter_set.update({"checkpoint": "RelCheckpoint1-1"})
    a = db.selected_stress_pks
    assert a.pop() == 1


def test_filtered_record():
    db.filter_set.clear()
    db.filter_set.update({"serial_number": "41C36MX9YSJM"})
    db.filter_set.update({"wip": "1675676"})
    a = list(db.filtered_record.records.values())
    assert a[0].get("SerialNumber") == "41C36MX9YSJM"

