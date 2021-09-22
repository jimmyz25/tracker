import datetime as dt
import functools
import os
import sqlite3
import sys
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
    def __init__(self, records: list):
        """
        :param records: a list of dict
        """
        self.records = records
        self.value_list = []

        # if records is not None:
        #     for record in records:
        #         self.value_list.append([dict(record).get(column) for column in self.col])

    # @functools.cached_property
    # def col(self):
    #     if self.records is not None:  # create a dict with sn as index
    #         one_row = dict(self.records[0])
    #         return list(one_row.keys())
    #     else:
    #         return [""]


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
                if value != "":
                    row.append(f' {key} LIKE \"{value}%\"')
            elif isinstance(value, int):
                row.append(f'{key} = {value}')
            elif isinstance(value, set):
                if len(value) > 1:
                    row.append(f'{key} in {tuple(value)}')
                elif len(value) == 1:
                    row.append(f'{key} = {value.pop()}')
            elif isinstance(value, tuple):
                if len(value) > 1:
                    row.append(f'{key} in {tuple(value)}')
                else:
                    row.append(f'{key} = {value[0]}')
        if len(row) == 0:
            sql = ""
        else:
            sql = "WHERE " + " AND ".join(row)

        return sql

    def __init__(self, address):
        self.__address__ = address
        self.__connect__()
        self.db_memory = sqlite3.connect(':memory:')
        self.con.backup(self.db_memory)
        self.current_table = "RelLog_T"

        self.filter_set = dict(
            {
                "config": None,
                "build": None,
                "program": None,
                "stress": None,
                "checkpoint": None,
                "serial_number": None,
                "serial_number_list": None,
                "wip": None,
                "failure_group": None,
                "failure_mode": None,
                "selected_row": None,
                "update_mode": None,
                "show_latest": None,
                "selected_pks": None,
                "station": None
            }
        )

    def clean_up_sn_list(self, sn_list: str):
        if isinstance(sn_list, str):
            temp1 = re.split(',', re.sub('[^a-zA-Z0-9.]', ',', sn_list))
            temp2 = [sn.strip().upper() for sn in temp1 if len(sn) > 0]
            res = []
            for i in temp2:
                if i not in res and not self.sn_exist(i):
                    res.append(i)
            self.filter_set.update({"serial_number_list": res})
            result = "\n".join(res)
            return result
        else:
            return ""

    @property
    def ready_to_add(self):
        a = 0
        b = 0
        c = 0
        ok_to_add = []
        duplicate = []
        if self.filter_set.get("serial_number_list") is None:
            return False
        for sn in self.filter_set.get("serial_number_list", []):
            if self.sn_exist(sn):
                duplicate.append(sn)
            else:
                ok_to_add.append(sn)
        if len(duplicate) == 0 and len(ok_to_add) > 0:
            c = 1
        if self.selected_config_pks is not None:
            a = len(self.selected_config_pks)
        if self.selected_stress_pks is not None:
            b = len(self.selected_stress_pks)
        return a == 1 and b == 1 and c == 1

    @property
    def ready_to_update(self):
        a = 0
        b = 0
        c = 0
        d = 0
        if self.filter_set.get("selected_pk") is not None:
            d = len(self.filter_set.get("selected_pk", []))
        if self.selected_config_pks is not None:
            a = len(self.selected_config_pks)
        if self.filter_set.get("serial_number") is not None:
            c = 1
        if self.selected_stress_pks is not None:
            b = len(self.selected_stress_pks)

        return a == 1 and b == 1 and c == 1 and d == 1

    @property
    def ready_to_checkin(self):
        # no duplicate SN is allowed, all SN needs to complete current checkpoint
        # TODO there is a bug, if SN hasn't checked out the latest checkpoint but
        # earier checkpoint is selected, then it'll allow user to check the SN to next checkpoint
        if self.filter_set.get("selected_pks") is not None:
            serial_number_list = []
            for pk in self.filter_set.get("selected_pks", []):
                sql = f"SELECT RelLog_T.PK,RelLog_T.SerialNumber, Config_SN_T.DateAdded,RelLog_T.EndTimestamp from RelLog_T  " \
                      "left join Config_SN_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and " \
                      " Config_SN_T.SerialNumber = RelLog_T.SerialNumber " \
                      "WHERE RelLog_T.PK = ?"
                result = self.cur.execute(sql, (pk,)).fetchone()
                sn = result["SerialNumber"]
                if sn in serial_number_list:
                    return False
                serial_number_list.append(result["SerialNumber"])
                if result["EndTimestamp"] is None or result["EndTimestamp"] == "":
                    # print (result["EndTimestamp"] )
                    return False
            return True

    @property
    def ready_to_checkout(self):
        return not self.ready_to_checkin

    @property
    def config_str(self):
        return " ".join([str(self.filter_set.get("program", "")),
                         str(self.filter_set.get("build", "")),
                         str(self.filter_set.get("config", ""))])

    @property
    def stress_str(self):
        return " ".join([str(self.filter_set.get("stress", "")), str(self.filter_set.get("checkpoint", ""))])

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
    def cache_failure_mode_of_sn_table(self):
        sql = f'SELECT PK,FailureGroup,FailureMode FROM FALog_T ' + \
              self.sql_filter_str({
                  "SerialNumber": self.filter_set.get("serial_number"),
                  "FK_RelStress": self.selected_stress_pks
              })
        results = self.cur.execute(sql).fetchall()
        if results is None:
            return [dict()]
        else:
            return [dict(result) for result in results]

    @property
    def selected_config_pks(self):
        if self.filter_set.get("program") is None and self.filter_set.get("build") is None \
                and self.filter_set.get("config") is None:
            return None
        else:
            sql = "SELECT PK FROM Config_T " + self.sql_filter_str({"Program": self.filter_set.get("program"),
                                                                    "Build": self.filter_set.get("build"),
                                                                    "Config": self.filter_set.get("config")})
            results = self.cur.execute(sql).fetchall()
            return set(result["PK"] for result in results)

    @property
    def selected_stress_pks(self):
        if self.filter_set.get("stress") is None and self.filter_set.get("checkpoint") is None:
            return None
        else:
            sql = "SELECT PK FROM RelStress_T " + self.sql_filter_str({"RelStress": self.filter_set.get("stress"),
                                                                       "RelCheckpoint": self.filter_set.get(
                                                                           "checkpoint")})
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
    def failure_mode_group_list(self):
        sql = "SELECT Distinct FailureGroup FROM FailureMode_T "
        results = self.cur.execute(sql).fetchall()
        return set(result["FailureGroup"] for result in results)

    @property
    def failure_mode_list_to_select(self):
        sql = "SELECT FailureMode FROM FailureMode_T  " + \
              self.sql_filter_str(({"FailureGroup": self.filter_set.get("failure_group")}))
        results = self.cur.execute(sql).fetchall()
        sql = "SELECT FailureMode From FALog_T " + self.sql_filter_str({
            "SerialNumber": self.filter_set.get("serial_number"),
            "FK_RelStress": self.selected_stress_pks
        })
        result_existing = self.cur.execute(sql).fetchall()
        all_failure_mode = set(result["FailureMode"] for result in results)
        existing = set(result["FailureMode"] for result in result_existing)
        return all_failure_mode - existing

    # @property
    # def str_selected_config(self):
    #     selected_pk = self.selected_config_pks
    #     if self.selected_config_pks:
    #         if len(selected_pk) == 1:
    #             first_config = ConfigModel(selected_pk.pop())
    #             return str(first_config)
    #         else:
    #             return "Multiple Configs"
    #     else:
    #         return "no config assigned"

    @property
    def filtered_record(self):
        table = self.current_table
        sql = f'SELECT SerialNumber,Station,WIP,StartTime,EndTime, RelStress_T.RelStress, RelStress_T.RelCheckpoint ' \
              f'FROM {table} ' \
              f'Inner Join RelStress_T ON {table}.FK_RelStress = RelStress_T.PK ' + \
              self.sql_filter_str({"WIP": self.filter_set.get("wip"),
                                   "SerialNumber": self.filter_set.get("serial_number"),
                                   "Config_FK": self.selected_config_pks,
                                   "FK_RelStress": self.selected_stress_pks}) + \
              ' LIMIT 50'
        results = self.cur.execute(sql).fetchall()
        return results

    @property
    def rel_log_table_view_data(self):
        sql = f'SELECT RelLog_T.PK,Config_T.Config, RelLog_T.WIP,RelLog_T.SerialNumber,' \
              f'Station,StartTime,EndTime, RelStress_T.RelStress, ' \
              f'RelStress_T.RelCheckpoint ' \
              f'FROM RelLog_T ' \
              f'  left Join RelStress_T ON RelLog_T.FK_RelStress = RelStress_T.PK ' + \
              f'  left Join Config_SN_T ON RelLog_T.SerialNumber = Config_SN_T.SerialNumber ' + \
              f'  left Join Config_T ON Config_SN_T.Config_FK = Config_T.PK ' + \
              self.sql_filter_str({"RelLog_T.WIP": self.filter_set.get("wip"),
                                   "RelLog_T.SerialNumber": self.filter_set.get("serial_number"),
                                   "Config_FK": self.selected_config_pks,
                                   "FK_RelStress": self.selected_stress_pks}) + \
              ' LIMIT 100'
        results = self.cur.execute(sql).fetchall()
        if results is None:
            return [dict()]
        else:
            return [dict(result) for result in results]

    @property
    def fa_log_table_view_data(self):
        sql = f'SELECT FALog_T.PK,Config_T.Config,FALog_T.SerialNumber,' \
              f'FALog_T.Station,FALog_T.StartTime,RelStress_T.RelStress, FALog_T.FailureMode,FALog_T.FailureGroup,' \
              f'RelStress_T.RelCheckpoint, FALog_T.FA_Details' \
              f' FROM FALog_T ' \
              f' Left Join RelStress_T ON FALog_T.FK_RelStress = RelStress_T.PK ' + \
              f' Left Join Config_SN_T ON FALog_T.SerialNumber = Config_SN_T.SerialNumber ' + \
              f' Left Join Config_T ON Config_SN_T.Config_FK = Config_T.PK ' + \
              self.sql_filter_str({"FALog_T.WIP": self.filter_set.get("wip"),
                                   "FALog_T.SerialNumber": self.filter_set.get("serial_number"),
                                   "Config_FK": self.selected_config_pks,
                                   "FailureMode": self.filter_set.get("failure_mode"),
                                   "FK_RelStress": self.selected_stress_pks}) + \
              ' LIMIT 100'
        results = self.cur.execute(sql).fetchall()
        if results is None:
            return [dict()]
        else:
            return [dict(result) for result in results]

    @property
    def latest_sn_history(self):
        sql = f"SELECT Config_SN_T.*, RelLog_T.StartTime, RelLog_T.EndTime, RelLog_T.Notes," \
              " RelLog_T.Notes,RelStress_T.RelStress,RelStress_T.RelCheckpoint from Config_SN_T  " \
              "left join RelLog_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and " \
              " Config_SN_T.SerialNumber = RelLog_T.SerialNumber " \
              "left join Config_T ON Config_T.PK = Config_SN_T.Config_FK " \
              "left join RelStress_T ON RelStress_T.PK = Config_SN_T.Stress_FK " + \
              self.sql_filter_str({"Config_SN_T.WIP": self.filter_set.get("wip"),
                                   "Config_SN_T.SerialNumber": self.filter_set.get("serial_number"),
                                   "Config_FK": self.selected_config_pks,
                                   "FK_RelStress": self.selected_stress_pks}) + \
              ' LIMIT 50'
        results = self.cur.execute(sql).fetchall()
        if results is None:
            return [dict()]
        else:
            return [dict(result) for result in results]

    @property
    def program_list(self):
        sql = "SELECT Distinct Program FROM Config_T "
        results = self.cur.execute(sql).fetchall()
        return set(result["Program"] for result in results)

    @property
    def build_list(self):
        sql = "SELECT Distinct Build FROM Config_T "
        results = self.cur.execute(sql).fetchall()
        return set(result["Build"] for result in results)

    @property
    def stress_list(self):
        sql = "SELECT Distinct RelStress FROM RelStress_T "
        results = self.cur.execute(sql).fetchall()
        return set(result["RelStress"] for result in results)

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
            return False
        if sn == "":
            return False
        else:
            # results = self.con.execute(f'SELECT SerialNumber FROM Config_SN_T WHERE SerialNumber like "{sn}%"') \
            #     .fetchmany(size=2)
            results = self.con.execute('SELECT SerialNumber FROM Config_SN_T WHERE SerialNumber = ?', (sn,)) \
                .fetchone()
            return results is not None

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

    def sync_sn_table(self, rows):
        for row in rows:
            if self.sn_exist(row["SerialNumber"]):
                sql = f'UPDATE Config_SN_T SET Config_FK= ?,DateAdded = ?,WIP=?,Stress_FK=? WHERE ' \
                      f'DateAdded<{row["DateAdded"]}' \
                      f' and SerialNumber = ?'
                self.cur.execute(sql,
                                 (row["Config_FK"], row["DateAdded"], row["WIP"],
                                  row["Stress_FK"],
                                  row["SerialNumber"]))
            else:
                self.cur.execute(f'INSERT INTO Config_SN_T (SerialNumber,Config_FK, Stress_FK, DateAdded, WIP)'
                                 f' VALUES (?,?,?,?,?)',
                                 (
                                     row["SerialNumber"], row["Config_FK"], row["Stress_FK"], row["DateAdded"],
                                     row["WIP"])
                                 )
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

    def insert_to_failure_log_table(self):
        current_time = dt.datetime.now().timestamp()
        time_str = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(self.filter_set.get("failure_mode"),list):
            for failure_mode in self.filter_set.get("failure_mode"):
                log = {
                    "FK_RelStress": self.selected_stress_pks.pop(),
                    "Station": self.filter_set.get('station'),
                    "SerialNumber": self.filter_set.get("serial_number"),
                    "FailureGroup": self.filter_set.get("failure_group"),
                    "FailureMode": failure_mode,
                    "StartTimestamp": current_time,
                    "StartTime":time_str,
                    "WIP": SnModel(self.filter_set.get("serial_number"),self).wip,
                    "removed":0
                }
                self.__insert_to_table__("FALog_T",**log)

    def delete_from_failure_log_table(self):
        if isinstance(self.filter_set.get("selected_pks"), list):
            for pk in self.filter_set.get("selected_pks"):
                sql = f"DELETE FROM FALog_T WHERE PK = {pk}"
                print (sql)
                self.cur.execute(sql)
            self.con.commit()


    # TODO: we can use delta from T0(earliest checkpoint) for each SN, to estimate time to complete a certain checkpoint

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

    def __insert_to_table__(self, tablename: str, **log):
        col_to_add = []
        values = []
        print(log)
        for col in self.__get_col_names__(tablename):
            values.append(log.get(col))
            col_to_add.append(col)
        cols_str = ",".join(col_to_add)
        values_tup = tuple(values)
        ques_mark = self.__construct_question_mark__(tablename)
        sql = "INSERT INTO " + tablename + " (" + cols_str + ") VALUES " + ques_mark
        print(sql)
        print(values_tup)
        try:
            self.cur.execute(sql, values_tup)
        except sqlite3.Error as e:
            print(e)
            return False
        self.con.commit()
        return True


class ConfigModel:
    def __init__(self, idx: int, database: DBsqlite = None):
        self.database = database
        self.id = idx

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, idx):
        self._id = None
        self._config_name = None
        self._build = None
        self._program = None
        sql = f'SELECT Config, Program, Build From Config_T WHERE PK = {idx}'
        if self.database:
            if self.database.config_exist(idx):
                result = self.database.cur.execute(sql).fetchone()
                self._id = idx
                self._config_name = result["Config"]
                self._build = result["Build"]
                self._program = result["Program"]

    def __str__(self):
        return " ".join([str(self.program), str(self.build), str(self.config_name)])

    @property
    def config_name(self):
        return self._config_name

    @property
    def unit_count(self):
        sql = f'SELECT COUNT (SerialNumber) as Unit_Count from Config_SN_T WHERE Config_FK = {self.id}'
        result = self.database.cur.execute(sql).fetchone()
        return result['Unit_Count']

    @property
    def program(self):
        return self._program

    @property
    def build(self):
        return self._build


class StressModel:
    def __init__(self, idx: int, database: DBsqlite = None):
        self.database = database
        self.id = idx

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, idx):
        self._id = None
        self._rel_stress = None
        self._rel_checkpoint = None
        sql = f'SELECT RelStress, RelCheckpoint From RelStress_T WHERE PK = {idx}'
        if self.database:
            if self.database.stress_exist(idx):
                result = self.database.cur.execute(sql).fetchone()
                self._id = idx
                self._rel_stress = result["RelStress"]
                self._rel_checkpoint = result["RelCheckpoint"]

    @property
    def rel_stress(self):
        return self._rel_stress

    @property
    def rel_checkpoint(self):
        return self._rel_checkpoint

    def __str__(self):
        return " ".join([str(self.rel_stress), str(self.rel_checkpoint)])


class SnModel:
    def __init__(self, sn: str, database: DBsqlite):
        self.database = database
        self.serial_number = sn

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, sn):
        self._serial_number = None
        self._config = ConfigModel(None, None)
        self._stress = StressModel(None, None)
        self._wip = None
        if not (sn is None or sn == ""):
            if self.database:
                if self.database.sn_exist(sn):
                    sql = f'SELECT SerialNumber,Config_FK, WIP, Stress_FK From Config_SN_T WHERE SerialNumber like "{sn}%"'
                    result = self.database.cur.execute(sql).fetchone()
                    self._serial_number = result["SerialNumber"]
                    self._config = ConfigModel(result["Config_FK"], self.database)
                    self._stress = StressModel(result["Stress_FK"], self.database)
                    self._wip = result["WIP"]

    @property
    def config(self):
        return self._config

    @property
    def stress(self):
        return self._stress

    @property
    def wip(self):
        return self._wip
