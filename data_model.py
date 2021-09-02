import datetime as dt
import functools
import os
import sqlite3
import sys
import pandas as pd



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
    def filter_func(x, parameter: str, value_set: set):
        if isinstance(value_set, set):
            if len(value_set) == 0:
                return True
            else:
                return x.get(parameter) in value_set
        else:
            if isinstance(value_set, str):
                return x.get(parameter).startswith(value_set)
            elif isinstance(value_set, int):
                return x.get(parameter) in {value_set}
            else:
                return True

    def __init__(self, address):
        self.__address__ = address
        self.__connect__()
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

    @functools.cached_property
    def cache_sn_table(self):
        return self.__create_cache_sn_table__()

    @functools.cached_property
    def cache_wip_table(self):
        return self.__create_cache_wip_table__()

    @functools.cached_property
    def cache_latest_sn_history(self):
        return self.__create_latest_sn_history__()

    @functools.cached_property
    def cache_rel_log(self):
        return self.__create_cache_rel_log__()

    @functools.cached_property
    def cache_stress_table(self):
        return self.__create_cache_stress_table__()

    @functools.cached_property
    def cache_config_table(self):
        return self.__create_cache_config_table__()

    @property
    def selected_config_pks(self):
        result = self.cache_config_table \
            .record_filter(self.filter_func, parameter="Program", value_set=self.filter_set.get("program")) \
            .record_filter(self.filter_func, parameter="Build", value_set=self.filter_set.get("build")) \
            .record_filter(self.filter_func, parameter="Config", value_set=self.filter_set.get("config")) \
            .records.values()
        result = [x.get("PK") for x in result]
        return set(result)

    @property
    def selected_stress_pks(self):
        result = self.cache_stress_table \
            .record_filter(self.filter_func, parameter="RelStress", value_set=self.filter_set.get("stress")) \
            .record_filter(self.filter_func, parameter="RelCheckpoint", value_set=self.filter_set.get("checkpoint")) \
            .records.values()
        result = [x.get("PK") for x in result]
        return set(result)

    @property
    def config_list_to_select(self):
        result = self.cache_config_table \
            .record_filter(self.filter_func, parameter="Program", value_set=self.filter_set.get("program")) \
            .record_filter(self.filter_func, parameter="Build", value_set=self.filter_set.get("build")) \
            .records.values()
        result = [x.get("Config") for x in result]
        return set(result)

    @property
    def ckp_list_to_select(self):
        result = self.cache_stress_table \
            .record_filter(self.filter_func, parameter="RelStress", value_set=self.filter_set.get("stress")) \
            .records.values()
        result = [x.get("RelCheckpoint") for x in result]
        return set(result)

    @property
    def filtered_record(self):
        if self.filter_set.get("filter_table") == "RelLog_T" and self.filter_set.get("latest") is False:
            record = self.cache_rel_log
        elif self.filter_set.get("filter_table") == "RelLog_T" and self.filter_set.get("latest") is True:
            record = self.cache_latest_sn_history
        else:
            record = self.cache_rel_log

        result = record.record_filter(self.filter_func, parameter="WIP", value_set=self.filter_set.get("wip")) \
            .record_filter(self.filter_func, parameter="SerialNumber", value_set=self.filter_set.get("serial_number")) \
            .record_filter(self.filter_func, parameter="Config_FK", value_set=self.selected_config_pks) \
            .record_filter(self.filter_func, parameter="FK_RelStress", value_set=self.selected_stress_pks)
        return result

    @property
    def program_list(self):
        program = [record.get("Program") for record in self.cache_config_table.records.values()]
        return set(program)

    @property
    def build_list(self):
        build = [record.get("Build") for record in self.cache_config_table.records.values()]
        return set(build)

    @property
    def stress_list(self):
        stress = [record.get("RelStress") for record in self.cache_stress_table.records.values()]
        return set(stress)

    def __create_cache_sn_table__(self):
        results = self.fetch("SELECT * from Config_SN_T")
        return RecordsDb(results, key="SerialNumber")

    def __create_cache_wip_table__(self):
        results = self.fetch("SELECT * FROM WIP_Status_T")
        return RecordsDb(results, key="WIP")

    def __create_cache_config_table__(self):
        results = self.fetch("SELECT * FROM Config_T")
        return RecordsDb(results, key="PK")

    def __create_cache_stress_table__(self):
        results = self.fetch("SELECT * FROM RelStress_T")
        return RecordsDb(results, key="PK")

    def __create_cache_rel_log__(self):
        results = self.fetch("SELECT RelLog_T.*,Config_SN_T.Config_FK,Config_SN_T.Stress_FK,"
                             " RelStress_T.RelStress, RelStress_T.RelCheckpoint "
                             "FROM RelLog_T "
                             "Inner Join Config_SN_T ON RelLog_T.SerialNumber = Config_SN_T.SerialNumber "
                             "Inner Join RelStress_T ON RelStress_T.Pk = Config_SN_T.Stress_FK "
                             "Inner Join Config_T ON Config_T.PK = Config_SN_T.Config_FK ")
        return RecordsDb(results, key="PK")

    def __create_latest_sn_history__(self):
        results = self.fetch("SELECT Config_SN_T.*, RelLog_T.StartTimestamp, RelLog_T.EndTimestamp,"
                             "RelLog_T.Notes from Config_SN_T "
                             "left join RelLog_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and "
                             " Config_SN_T.SerialNumber = RelLog_T.SerialNumber "
                             "left join Config_T ON Config_T.PK = Config_SN_T.Config_FK "
                             "left join RelStress_T ON RelStress_T.PK = Config_SN_T.Stress_FK ")
        return RecordsDb(results, key="SerialNumber")

    def clear_cache(self,cache_name):
        if hasattr( object, cache_name ):
            delattr(self, cache_name)
        else:
            print(cache_name," doesn't exist")

    def __connect__(self):
        self.con = sqlite3.connect(self.__address__)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def __disconnect__(self):
        self.con.close()

    def fetch(self, sql):
        # self.cur.execute(sql)
        # result = self.cur.fetchall()
        result = pd.read_sql_query(sql, self.con)
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
        return sn.upper() in self.cache_sn_table.records.keys()

    def wip_exist(self, wip):
        """
        :param wip: "string"
        :return: bool
        """
        if not isinstance(wip, str):
            raise TypeError
        return wip.upper() in self.cache_wip_table.records.keys()

    def config_exist(self, idx):
        """
        :param idx: "int"
        :return: bool
        """
        if not isinstance(idx, int):
            raise TypeError
        return idx in self.cache_config_table.records.keys()

    def stress_exist(self, idx):
        """
        :param idx: "int"
        :return: bool
        """
        if not isinstance(idx, int):
            raise TypeError
        return idx in self.cache_stress_table.records.keys()

    def get_sn_row(self, pk):
        result = self.cur.execute("SELECT Config_FK,Stress_FK,WIP,DateAdded,SerialNumber from Config_SN_T"
                                  " WHERE PK = ? ", (pk,)).fetchone()
        if result is not None:
            return dict(result)
        else:
            return None

    def get_config(self, idx):
        result = self.cur.execute("SELECT Program,Build,Config from Config_T WHERE PK = ?", (idx,)).fetchone()
        if result is None:
            return dict()
        else:
            return dict(result)

    def sync_sn_table(self, rows):
        for sn, row in rows.records.items():
            if self.sn_exist(sn):
                sql = f'UPDATE Config_SN_T SET Config_FK= ?,DateAdded = ?,WIP=?,Stress_FK=? WHERE ' \
                      f'DateAdded<{row.get("DateAdded")}' \
                      f' and SerialNumber = ?'
                self.cur.execute(sql,
                                 (row.get("Config_FK"), row.get("DateAdded"), row.get("DateAdded"),
                                  row.get("Stress_FK"),
                                  sn))
            else:
                self.cur.execute(f'INSERT INTO Config_SN_T (SerialNumber,Config_FK, Stress_FK, DateAdded, WIP)'
                                 f' VALUES (?,?,?,?,?)',
                                 (sn, row.get("Config_FK"), row.get("Stress_FK"), row.get("DateAdded"), row.get("WIP")))
        self.con.commit()
        return True

    def sync_wip_table(self, rows):
        for wip, row in rows.records.items():
            if self.wip_exist(wip):
                sql = f'UPDATE WIP_Status_T SET TimeStamp= ?,FK_RelStress=? WHERE ' \
                      f'WIP_Status_T.TimeStamp<{row.get("TimeStamp")}' \
                      f' and WIP = ?'
                self.cur.execute(sql, (row.get("TimeStamp"), row.get("FK_RelStress"), wip))
            else:
                self.cur.execute(f'INSERT INTO WIP_Status_T (WIP, TimeStamp, FK_RelStress)'
                                 f' VALUES (?,?,?)',
                                 (row.get("WIP"), row.get("TimeStamp"), row.get("FK_RelStress")))
        self.con.commit()
        return True

    def sync_config_table(self, rows):
        for configid, row in rows.records.items():
            if not self.config_exist(configid):
                sql = f'INSERT INTO Config_T (PK, Program, Build, Config, Notes) Values (?,?,?,?,?)'
                self.cur.execute(sql, (
                    row.get("PK"), row.get("Program"), row.get("Build"), row.get("Config"), row.get("Notes")))
            else:
                assert row.get("Config") == self.cache_config_table.records.get(configid).get("Config")
        self.con.commit()
        return True

    def sync_stress_table(self, rows):
        for stressid, row in rows.records.items():
            if not self.stress_exist(stressid):
                sql = f'INSERT INTO RelStress_T (PK, RelStress, RelCheckpoint,DaysTillReachCheckpoint,' \
                      f'removed,seqence) Values (?,?,?,?,?,?)'
                self.cur.execute(sql,
                                 (row.get("PK"), row.get("RelStress"), row.get("RelCheckpoint"),
                                  row.get("DaysTillReachCheckpoint"), row.get("removed"), row.get("seqence")))
            else:
                assert row.get("RelCheckpoint") == self.cache_stress_table.records.get(stressid).get("RelCheckpoint")
        self.con.commit()
        return True

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
        self.id = idx
        self.database = database

    @property
    def config_name(self):
        return self.database.cache_config_table.records.get(self.id).get("Config")

    @property
    def program(self):
        return self.database.cache_config_table.records.get(self.id).get("Program")

    @property
    def build(self):
        return self.database.cache_config_table.records.get(self.id).get("Build")


class StressModel:
    def __init__(self, idx: int, database: DBsqlite):
        self.id = idx
        self.database = database

    @property
    def rel_stress(self):
        return self.database.cache_stress_table.records.get(self.id).get("RelStress")

    @property
    def rel_checkpoint(self):
        return self.database.cache_stress_table.records.get(self.id).get("RelCheckpoint")


class SnModel:
    def __init__(self, sn: str, database: DBsqlite):
        self.serial_number = sn
        self.database = database

    @property
    def config(self):
        config_pk = self.database.cache_sn_table.records.get(self.serial_number).get("Config_FK")
        return ConfigModel(config_pk, self.database)

    @property
    def stress(self):
        stress_pk = self.database.cache_sn_table.records.get(self.serial_number).get("Stress_FK")
        return StressModel(stress_pk, self.database)
