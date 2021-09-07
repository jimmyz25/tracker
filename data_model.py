import datetime as dt
import functools
import os
import sqlite3
import sys
import pandas as pd
import timeit
import re

golden = 'temp.db'
RMD = "ReliabilityManagementDB.db"
ini_file = "CONFIG.ini"
golden_output = "golden.db"
create_db_sql = "create_db_sql.sql"

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
else:
    application_path = os.path.dirname(__file__)

golden = os.path.join(application_path, golden)
RMD = os.path.join(application_path, RMD)
ini_file = os.path.join(application_path, ini_file)
golden_output = os.path.join(application_path, golden_output)
create_db_sql = os.path.join(application_path, create_db_sql)


class RecordsDb:
    def __init__(self, records: list, key, sort_func=None):
        """
        :param records: a list of dict
        :param key:
        :param sort_func: if sort_func is provided, only the last will be saved with a same key
        """
        if records is not None:  # create a dict with sn as index
            if sort_func is not None:
                records.sort(key=sort_func)
            a = {dict(result).get(key): dict(result) for result in records}
            self.records = dict(a)
        else:
            self.records = dict()
        self.key = key

    def record_filter(self, func, **kwargs):
        records = list(filter(lambda x: func(x, **kwargs), self.records.values()))
        return RecordsDb(records, key=self.key)

    def key_filter(self, value):
        keys = list(filter(lambda x: x == value, self.records))
        records = [self.records.get(key) for key in keys]
        return RecordsDb(records, key=self.key)


# noinspection SpellCheckingInspection
class DBsqlite:
    """
    this is a database model to handle all database related operations, silver station will sync with gold station based
     on timestamp.
    """

    @staticmethod
    def sql_filter_str(kwp: dict):
        row = []
        for key, value in kwp.items():
            if isinstance(value, str):
                value.strip().strip("%")
                row.append(f' {key} LIKE \"{value}%\"')
            elif isinstance(value, int):
                row.append(f'{key} = {value}')
            elif isinstance(value, tuple):
                row.append(f'{key} in {value}')
        if any(kwp.values()):
            sql = "WHERE " + " AND".join(row)
        else:
            sql = " AND".join(row)
        return sql

    def __init__(self, address):
        self.__address__ = address
        self.__connect__()
        self.db_memory = sqlite3.connect(':memory:')
        self.con.backup(self.db_memory)

        self.filter_set = dict(
            {
                "config": None,
                "build": None,
                "program": None,
                "stress": None,
                "checkpoint": None,
                "serial_number": None,
                "wip": None,
                "filter_table": "RelLog_T",
                "latest": False
            }
        )

    @property
    def cache_sn_table(self):
        sql = f'SELECT * FROM Config_SN_T ORDER BY DateAdded DESC LIMIT 50000'
        results = self.cur.execute(sql).fetchall()
        return results

    @property
    def cache_config_table(self):
        sql = f'SELECT * FROM Config_T'
        results = self.cur.execute(sql).fetchall()
        return results

    @property
    def cache_wip_table(self):
        sql = f'SELECT * FROM WIP_Status_T'
        results = self.cur.execute(sql).fetchall()
        return results

    @property
    def cache_stress_table(self):
        sql = f'SELECT * FROM RelStress_T'
        results = self.cur.execute(sql).fetchall()
        return results

    @property
    def cache_rel_log_table(self, timestamp: float = 0):
        sql = f'SELECT * FROM RelLog_T WHERE StartTimestamp>{timestamp}'
        results = self.cur.execute(sql).fetchall()
        return results

    @property
    def selected_config_pks(self):
        sql = "SELECT PK FROM Config_T " + self.sql_filter_str({"Program": self.filter_set.get("program"),
                                                                "Build": self.filter_set.get("build"),
                                                                "Config": self.filter_set.get("config")})
        results = self.cur.execute(sql).fetchall()
        return set(result["PK"] for result in results)

    @property
    def selected_stress_pks(self):
        sql = "SELECT PK FROM RelStress_T " + self.sql_filter_str({"RelStress": self.filter_set.get("stress"),
                                                                   "RelCheckpoint": self.filter_set.get("checkpoint")})
        results = self.cur.execute(sql).fetchall()
        return set(result["PK"] for result in results)

    @property
    def config_list_to_select(self):
        sql = "SELECT Config FROM Config_T " + self.sql_filter_str({"Program": self.filter_set.get("program"),
                                                                    "Build": self.filter_set.get("build")})
        results = self.cur.execute(sql).fetchall()
        return set(result["Config"] for result in results)

    @property
    def ckp_list_to_select(self):
        sql = "SELECT RelCheckpoint FROM RelStress_T " + \
              self.sql_filter_str({"RelStress": self.filter_set.get("stress")})
        results = self.cur.execute(sql).fetchall()
        return set(result["RelCheckpoint"] for result in results)

    @property
    def filtered_record(self):
        table = self.filter_set.get("filter_table")
        sql = f'SELECT SerialNumber FROM {table} ' + \
              self.sql_filter_str({"WIP": self.filter_set.get("wip"),
                                   "SerialNumber": self.filter_set.get("serial_number"),
                                   "Config_FK": self.selected_config_pks,
                                   "FK_RelStress": self.selected_stress_pks}) + \
              ' LIMIT 100'
        results = self.cur.execute(sql).fetchall()
        return results

    @functools.cached_property
    def program_list(self):
        sql = "SELECT Distinct Program FROM Config_T "
        results = self.cur.execute(sql).fetchall()
        return set(result["Program"] for result in results)

    @functools.cached_property
    def build_list(self):
        sql = "SELECT Distinct Build FROM Config_T "
        results = self.cur.execute(sql).fetchall()
        return set(result["Build"] for result in results)

    @functools.cached_property
    def stress_list(self):
        sql = "SELECT Distinct RelStress FROM RelStress_T "
        results = self.cur.execute(sql).fetchall()
        return set(result["RelStress"] for result in results)

    def __create_latest_sn_history__(self):
        results = self.fetch("SELECT Config_SN_T.*, RelLog_T.StartTimestamp, RelLog_T.EndTimestamp,"
                             "RelLog_T.Notes from Config_SN_T "
                             "left join RelLog_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and "
                             " Config_SN_T.SerialNumber = RelLog_T.SerialNumber "
                             "left join Config_T ON Config_T.PK = Config_SN_T.Config_FK "
                             "left join RelStress_T ON RelStress_T.PK = Config_SN_T.Stress_FK ")
        return RecordsDb(results, key="SerialNumber")

    def __connect__(self):
        self.con = sqlite3.connect(self.__address__)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def __disconnect__(self):
        self.con.close()

    def fetch(self, sql):
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def execute(self, sql):
        self.cur.execute(sql)

    def sn_exist(self, sn):
        """
        :param sn: "string"
        :return: bool
        """
        if not isinstance(sn, str):
            raise TypeError
        result = self.con.execute(f'SELECT SerialNumber FROM Config_SN_T WHERE SerialNumber =?', (sn,)).fetchone()
        return result is not None

    def wip_exist(self, wip):
        """
        :param wip: "string"
        :return: bool
        """
        if not isinstance(wip, str):
            raise TypeError
        result = self.db_memory.execute(f'SELECT WIP FROM WIP_Status_T WHERE WIP =? LIMIT 1', (wip,)).fetchone()
        return result is not None
        # return wip.upper() in self.cache_wip_table.records.keys()

    def config_exist(self, idx):
        """
        :param idx: "int"
        :return: bool
        """
        if not isinstance(idx, int):
            raise TypeError
        # return idx in self.cache_config_table.records.keys()
        result = self.con.execute(f'SELECT PK FROM Config_T WHERE PK =?', (idx,)).fetchone()
        return result is not None

    def stress_exist(self, idx):
        """
        :param idx: "int"
        :return: bool
        """
        if not isinstance(idx, int):
            raise TypeError
        # return idx in self.cache_stress_table.records.keys()
        result = self.con.execute(f'SELECT PK FROM RelStress_T WHERE PK =?', (idx,)).fetchone()
        return result is not None

    # def get_config(self, idx):
    #     result = self.cur.execute("SELECT Program,Build,Config from Config_T WHERE PK = ?", (idx,)).fetchone()
    #     if result is None:
    #         return dict()
    #     else:
    #         return dict(result)

    def sync_sn_table(self, rows):
        for row in rows:
            if self.sn_exist(row["SerialNumber"]):
                sql = f'UPDATE Config_SN_T SET Config_FK= ?,DateAdded = ?,WIP=?,Stress_FK=? WHERE ' \
                      f'DateAdded<{row["DateAdded"]}' \
                      f' and SerialNumber = ?'
                # print( (row["Config_FK"], row["DateAdded"], row["WIP"],
                #                   row["Stress_FK"],
                #                   row["SerialNumber"]))
                self.cur.execute(sql,
                                 (row["Config_FK"], row["DateAdded"], row["WIP"],
                                  row["Stress_FK"],
                                  row["SerialNumber"]))
            else:
                self.cur.execute(f'INSERT INTO Config_SN_T (SerialNumber,Config_FK, Stress_FK, DateAdded, WIP)'
                                 f' VALUES (?,?,?,?,?)',
                                 (
                                 row["SerialNumber"], row["Config_FK"], row["Stress_FK"], row["DateAdded"], row["WIP"]))
        self.con.commit()
        return True

    def sync_wip_table(self, rows):
        for row in rows:
            if self.wip_exist(row["WIP"]):
                sql = f'UPDATE WIP_Status_T SET TimeStamp= ?,FK_RelStress=? WHERE ' \
                      f'WIP_Status_T.TimeStamp<{row["TimeStamp"]}' \
                      f' and WIP = ?'
                self.cur.execute(sql, (row["TimeStamp"], row["FK_RelStress"], row["WIP"]))
            else:
                self.cur.execute(f'INSERT INTO WIP_Status_T (WIP, TimeStamp, FK_RelStress)'
                                 f' VALUES (?,?,?)',
                                 (row["WIP"], row["TimeStamp"], row["FK_RelStress"]))
        self.con.commit()
        return True

    def sync_config_table(self, rows):
        for row in rows:
            if not self.config_exist(row["PK"]):
                sql = f'INSERT INTO Config_T (PK, Program, Build, Config, Notes) Values (?,?,?,?,?)'
                self.cur.execute(sql, (
                    row["PK"], row["Program"], row["Build"], row["Config"], row["Notes"]))
            else:
                config_name = self.cur.execute("SELECT Config From Config_T WHERE PK = ?", (row["PK"],)).fetchone()
                assert row["Config"] == config_name["Config"]
        self.con.commit()
        return True

    def sync_stress_table(self, rows):
        for row in rows:
            if not self.stress_exist(row["PK"]):
                sql = f'INSERT INTO RelStress_T (PK, RelStress, RelCheckpoint,DaysTillReachCheckpoint,' \
                      f'removed,seqence) Values (?,?,?,?,?,?)'
                self.cur.execute(sql,
                                 (row["PK"], row["RelStress"], row["RelCheckpoint"],
                                  row["DaysTillReachCheckpoint"], row["removed"], row["seqence"]))
            else:
                checkpoint_name = self.cur.execute("SELECT RelCheckpoint From RelStress_T WHERE PK = ?", (row['PK'],)) \
                    .fetchone()
                assert row["RelCheckpoint"] == checkpoint_name["RelCheckpoint"]
        self.con.commit()
        return True

    def sync_rel_log_table(self, rows):
        # make SN + starttime unique index, insert or ignore from A to B, then insert or ignore from B to A
        for row in rows:
            sql = f'INSERT or IGNORE INTO RelLog_T (SerialNumber,Station,WIP,StartTimestamp,' \
                  f'EndTimestamp,StartTime,EndTime,Notes,removed,FK_Tagger,FK_RelStress)' \
                  f' Values (?,?,?,?,?,?,?,?,?,?,?)'
            self.cur.execute(sql,
                             (row["SerialNumber"], row["Station"], row["WIP"], row["StartTimestamp"],
                              row["EndTimestamp"], row["StartTime"], row["EndTime"], row["Notes"],
                              row["removed"], row["FK_Tagger"], row["FK_RelStress"]))
        self.con.commit()
        return True
        pass

    # TODO: we can use delta from T0(earliest checkpoint) for each SN, to estimate time to complete a certain checkpoint
    def time_needed(self):
        pass

    def add_description(self, records: dict):
        pass

    def __get_col_names__(self, table_name):
        cols = []
        pragma = self.cur.execute("PRAGMA table_info({})".format(table_name)).fetchall()
        for row in pragma:
            cols.append(row["name"])
        return cols

    def __construct_question_mark__(self, table_name):
        cols = self.__get_col_names__(table_name)
        column_count = len(cols)
        question_marks = "(" + ",".join(["?" for _ in range(column_count)]) + ")"
        return question_marks

    def insert_to_table(self, log: dict, tablename: str):
        print("prepare to insert to {}".format(tablename))
        """log's type is Log object"""
        col_to_add = []
        values = []
        for col in self.__get_col_names__(tablename):
            values.append(log.get(col))
            col_to_add.append(col)
        cols_str = ",".join(col_to_add)
        values_tup = tuple(values)
        ques_mark = self.__construct_question_mark__(tablename)
        sql = "INSERT INTO " + tablename + " (" + cols_str + ") VALUES " + ques_mark
        try:
            self.cur.execute(sql, values_tup)
        except sqlite3.Error as e:
            print(e)
            return False
        self.con.commit()
        print("log data successfully")
        return True


class ConfigModel:
    def __init__(self, idx: int, database: DBsqlite):
        self.database = database
        self.id = idx

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, idx):
        sql = f'SELECT Config, Program, Build From Config_T WHERE PK = {idx}'
        if self.database.config_exist(idx):
            result = self.database.cur.execute(sql).fetchone()
            self._id = idx
            self._config_name = result["Config"]
            self._build = result["Build"]
            self._program = result["Program"]
        else:
            self._id = None
            self._config_name = None
            self._build = None
            self._program = None

    @property
    def config_name(self):
        return self._config_name

    @property
    def program(self):
        return self._program

    @property
    def build(self):
        return self._build


class StressModel:
    def __init__(self, idx: int, database: DBsqlite):
        self.database = database
        self.id = idx

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, idx):
        sql = f'SELECT RelStress, RelCheckpoint From RelStress_T WHERE PK = {idx}'
        if self.database.stress_exist(idx):
            result = self.database.cur.execute(sql).fetchone()
            self._id = idx
            self._rel_stress = result["RelStress"]
            self._rel_checkpoint = result["RelCheckpoint"]
        else:
            self._id = None
            self._rel_stress = None
            self._rel_checkpoint = None

    @property
    def rel_stress(self):
        return self._rel_stress

    @property
    def rel_checkpoint(self):
        return self._rel_checkpoint


class SnModel:
    def __init__(self, sn: str, database: DBsqlite):
        self.database = database
        self.serial_number = sn

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, sn):
        sql = f'SELECT Config_FK, WIP, Stress_FK From Config_SN_T WHERE SerialNumber = "{sn}"'
        if self.database.sn_exist(sn):
            result = self.database.cur.execute(sql).fetchone()
            self._serial_number = sn
            self._config = ConfigModel(result["Config_FK"], self.database)
            self._stress = StressModel(result["Stress_FK"], self.database)
            self._wip = result["WIP"]
        else:
            self._serial_number = sn
            self._config = None
            self._stress = None
            self._wip = None

    @property
    def config(self):
        return self._config

    @property
    def stress(self):
        return self._stress

    @property
    def wip(self):
        return self._wip
