import datetime as dt
# import os
import sqlite3
# import sys
import re
import uuid
# import random
import string
import secrets


# noinspection SpellCheckingInspection

class DBsqlite:
    """
    this is a database model to handle all database related operations, silver station will sync with gold station based
     on timestamp.
     station can be treated as user. station can read all but only have write access to row with same statio
    """

    def generate_random_sn(self):
        a_lot_of_sn = [str("".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
                       for _ in range(100)]
        self.filter_set.update({"serial_number_list": a_lot_of_sn})

    def sql_filter_str(self, kwp: dict, final=True, strict=False):
        row = []
        for key, value in kwp.items():
            if isinstance(value, str):
                if value.lower() == "none":
                    row.append(f'{key} is Null ')
                elif value.lower() == "not none":
                    row.append(f'{key} is not Null ')
                else:
                    value.strip().strip("%")
                    if value != "":
                        if strict:
                            row.append(f' {key} = \"{value}\"')
                        else:
                            row.append(f' {key} LIKE \"{value}%\"')
            elif isinstance(value, int):
                if value == -999:
                    row.append(f'{key} is Null')
                else:
                    row.append(f'{key} = {value}')
            elif isinstance(value, set) or isinstance(value, list):
                if len(value) > 1:
                    row.append(f'{key} in {tuple(value)}')
                elif len(value) == 1:
                    row.append(self.sql_filter_str({key: list(value)[0]}, final=False, strict=strict))
            elif isinstance(value, tuple):
                if len(value) > 1:
                    row.append(f'{key} in {tuple(value)}')
                elif len(value) == 1:
                    row.append(self.sql_filter_str({key: value[0]}, final=False, strict=strict))
        if final:
            row = list(filter(lambda x: x != "", row))
            if len(row) == 0:
                sql = ""
            else:
                sql = " WHERE " + " AND ".join(row)
        else:
            if len(row) == 0:
                sql = ""
            else:
                sql = " AND ".join(row)

        return sql

    def __init__(self, address, station=None):
        print(address)
        if DBsqlite.ok2use(address):
            self.__address__ = address
            self.__connect__()
            self.station = station
            self.db_memory = sqlite3.connect(':memory:')
            # self.con.backup(self.db_memory)
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
                    "selected_pks": None,
                    "station": None,
                    "note": None,
                    "file_creation_time": None
                }
            )
            self.display_setting = dict(
                {
                    "update_mode": None,
                    "show_latest": None,
                    "station_filter": None,
                }
            )
            self.printout = None
            # self.cur.execute("UPDATE RelLog_T SET removed = a  WHERE  PK = \"aa\"")

    @classmethod
    def ok2use(cls, address):
        try:
            con = sqlite3.connect(address)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM RelLog_T LIMIT 1")
            con.close()
            return True
        except sqlite3.Error:
            return False

    @property
    def station(self):
        return self._station

    def delete_trigger(self):
        del_trigger = f"""
                        DROP TRIGGER IF EXISTS Row_Security_Trigger_UPDATE_RELLOG;
                        DROP TRIGGER IF EXISTS Row_Security_Trigger_DELETE_RELLOG;
                        DROP TRIGGER IF EXISTS Row_Security_Trigger_UPDATE_FALLOG;
                        DROP TRIGGER IF EXISTS Row_Security_Trigger_DELETE_FALLOG;
                        """
        self.con.executescript(del_trigger)

    @station.setter
    def station(self, station_name: str = None):
        if isinstance(station_name, str):
            row_security_trigger = f"""
                DROP TRIGGER IF EXISTS Row_Security_Trigger_UPDATE_RELLOG;

                CREATE Trigger Row_Security_Trigger_UPDATE_RELLOG
                BEFORE UPDATE ON RelLog_T
                FOR EACH ROW
                WHEN old.Station <> \"{station_name}\"
                BEGIN
                    SELECT
                        CASE
                            WHEN TRUE THEN
                                RAISE (ABORT,'Not Your Data, Read Only')
                        END;
                END;

                DROP TRIGGER IF EXISTS Row_Security_Trigger_DELETE_RELLOG;
                CREATE Trigger Row_Security_Trigger_DELETE_RELLOG
                BEFORE DELETE ON RelLog_T
                FOR EACH ROW
                WHEN old.Station <> \"{station_name}\"
                BEGIN
                    SELECT
                        CASE
                            WHEN TRUE THEN
                                RAISE (ABORT,'Not Your Data, Read Only')
                        END;
                END;

                DROP TRIGGER IF EXISTS Row_Security_Trigger_UPDATE_FALLOG;
                CREATE Trigger Row_Security_Trigger_UPDATE_FALLOG
                BEFORE UPDATE ON FALog_T
                FOR EACH ROW
                WHEN old.Station <> \"{station_name}\"
                BEGIN
                    SELECT
                        CASE
                            WHEN TRUE THEN
                                RAISE (ABORT,'Not Your Data, Read Only')
                        END;
                END;

                DROP TRIGGER IF EXISTS Row_Security_Trigger_DELETE_FALLOG;
                CREATE Trigger Row_Security_Trigger_DELETE_FALLOG
                BEFORE DELETE ON FALog_T
                FOR EACH ROW
                WHEN old.Station <> \"{station_name}\"
                BEGIN
                    SELECT
                        CASE
                            WHEN TRUE THEN
                                RAISE (ABORT,'Not Your Data, Read Only')
                        END;
                END;
                """
            self.con.executescript(row_security_trigger)
            self._station = station_name
        else:
            self._station = None

    def clean_up_sn_list(self, sn_list: str):
        if isinstance(sn_list, str):
            temp1 = re.split(',', re.sub('[^a-zA-Z0-9.]', ',', sn_list))
            temp2 = [sn.strip().upper() for sn in temp1 if len(sn) > 0]
            res = []
            for i in temp2:
                if i not in res:
                    res.append(i)
            self.filter_set.update({"serial_number_list": res})
            result = "\n".join(res)
            return result
        else:
            return ""

    def get_test_history(self, sn: str):
        """
        check sn test history in Rel log and place in reverse
        :param sn:
        :return:
        """
        if self.sn_exist(sn):
            sql = " SELECT WIP, StartTimestamp, FK_RelStress from RelLog_T where SerialNumber = ? and removed = 0" \
                  " ORDER BY StartTimestamp DESC"
            result = self.cur.execute(sql, (sn,)).fetchall()
            if result:
                return [list(row) for row in result]

    def rel_tagging(self, sn: str, timestamp: float):
        history = self.get_test_history(sn)
        if history:
            for log in history:
                if timestamp > log[1]:
                    return log
            return [None, None, None]


    @property
    def ready_to_data_tagging(self):
        result = self.cur.execute("SELECT PK FROM Tagger_Log_T WHERE EndTimestamp is Null").fetchone()
        return result is None

    @property
    def ready_to_add(self):
        a = 0
        b = 0
        c = 0
        unknown_sn = []
        existed_sn = []
        if self.filter_set.get("serial_number_list") is None:
            return False
        for sn in self.filter_set.get("serial_number_list", []):
            if self.sn_exist(sn):
                existed_sn.append(sn)
            else:
                unknown_sn.append(sn)
        if len(existed_sn) == 0 and len(unknown_sn) > 0:
            c = 1
        if self.selected_config_pks is not None:
            a = len(self.selected_config_pks)
        if self.selected_stress_pks is not None:
            b = len(self.selected_stress_pks)
        return a == 1 and b == 1 and c == 1

    @property
    def ready_to_batch_update(self):
        c = 0
        unknown_sn = []
        existed_sn = []
        if self.filter_set.get("serial_number_list") is None:
            return False
        for sn in self.filter_set.get("serial_number_list", []):
            if self.sn_exist(sn):
                existed_sn.append(sn)
            else:
                unknown_sn.append(sn)
        if len(existed_sn) > 0 and len(unknown_sn) == 0:
            c = 1
        return c == 1

    @property
    def ready_to_update(self):
        a = 0
        b = 0
        c = 0
        d = 0
        if self.filter_set.get("selected_pks") is not None:
            d = len(self.filter_set.get("selected_pks", []))
        if self.selected_config_pks is not None:
            a = len(self.selected_config_pks)
        if self.filter_set.get("serial_number") is not None:
            c = 1
        if self.selected_stress_pks is not None:
            b = len(self.selected_stress_pks)
        return a == 1 and b == 1 and c == 1 and d == 1

    @property
    def ready_to_checkin(self):
        # latest and Endtimestamp is not None
        if self.cur is None:
            return False
        if self.filter_set.get("selected_pks") is not None:
            serial_number_list = []
            for pk in self.filter_set.get("selected_pks", []):
                sql = " SELECT SerialNumber, EndTimestamp FROM RelLog_T WHERE PK = ?"
                result = self.cur.execute(sql, (pk,)).fetchone()
                if result is None:
                    return False
                sn = result["SerialNumber"]
                if sn in serial_number_list:
                    return False
                serial_number_list.append(result["SerialNumber"])
                if result["EndTimestamp"] is None or result["EndTimestamp"] == "":
                    return False
                if not SnModel(sn, self).is_latest_row(pk):
                    return False

            return True

    @property
    def ready_to_checkout(self):
        # latest and Endtimestamp is None
        if self.cur is None:
            return False
        if self.filter_set.get("selected_pks") is not None:
            serial_number_list = []
            for pk in self.filter_set.get("selected_pks", []):
                sql = " SELECT SerialNumber, EndTimestamp FROM RelLog_T WHERE PK = ?"
                result = self.cur.execute(sql, (pk,)).fetchone()
                if result is None:
                    return False
                sn = result["SerialNumber"]
                if sn in serial_number_list:
                    return False
                serial_number_list.append(result["SerialNumber"])
                if result["EndTimestamp"]:
                    return False
                if not SnModel(sn, self).is_latest_row(pk):
                    return False
            return True

    @property
    def config_str(self):
        return " ".join([str(self.filter_set.get("program", "")),
                         str(self.filter_set.get("build", "")),
                         str(self.filter_set.get("config", ""))])

    @property
    def stress_str(self):
        return " ".join([str(self.filter_set.get("stress", "")), str(self.filter_set.get("checkpoint", ""))])

    # @property
    # def cache_sn_table(self):
    #     sql = f'SELECT * FROM Config_SN_T ORDER BY DateAdded DESC LIMIT 50000'
    #     results = self.cur.execute(sql).fetchall()
    #     return results

    # @property
    # def cache_config_table(self):
    #     sql = f'SELECT * FROM Config_T'
    #     results = self.cur.execute(sql).fetchall()
    #     return results
    #
    # @property
    # def cache_wip_table(self):
    #     sql = f'SELECT * FROM WIP_Status_T'
    #     results = self.cur.execute(sql).fetchall()
    #     return results
    #
    # @property
    # def cache_stress_table(self):
    #     sql = f'SELECT * FROM RelStress_T'
    #     results = self.cur.execute(sql).fetchall()
    #     return results

    @property
    def cache_rel_log_table(self, timestamp: float = 0):
        sql = f'SELECT * FROM RelLog_T WHERE StartTimestamp>{timestamp} and removed = 0'
        results = self.cur.execute(sql).fetchall()
        return results

    @property
    def cache_failure_mode_of_sn_table(self):
        sql = f'SELECT PK,FailureGroup,FailureMode,FA_Details FROM FALog_T ' + \
              self.sql_filter_str({
                  "SerialNumber": self.filter_set.get("serial_number"),
                  "FK_RelStress": self.selected_stress_pks,
                  "removed": 0
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
    def all_config_pks(self):
        sql = "SELECT PK FROM Config_T"
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
    def all_stress_pks(self):
        sql = "SELECT PK FROM RelStress_T"
        results = self.cur.execute(sql).fetchall()
        return set(result["PK"] for result in results)

    @property
    def config_list_to_select(self):
        if self.cur:
            sql = "SELECT Config FROM Config_T " + self.sql_filter_str({"Program": self.filter_set.get("program"),
                                                                        "Build": self.filter_set.get("build")})
            results = self.cur.execute(sql).fetchall()
            return set(result["Config"] for result in results)
        return None

    @property
    def ckp_list_to_select(self):
        sql = "SELECT RelCheckpoint FROM RelStress_T " + \
              self.sql_filter_str({
                  "RelStress": self.filter_set.get("stress"),
                  "removed": 0
              })
        results = self.cur.execute(sql).fetchall()
        return set(result["RelCheckpoint"] for result in results)

    @property
    def failure_mode_group_list(self):
        sql = "SELECT Distinct FailureGroup FROM FailureMode_T WHERE removed = 0 "
        results = self.cur.execute(sql).fetchall()
        return set(result["FailureGroup"] for result in results)

    @property
    def failure_mode_list_to_add_to_sn(self):
        if self.cur:
            sql = "SELECT FailureMode From FALog_T " + self.sql_filter_str({
                "SerialNumber": self.filter_set.get("serial_number"),
                "FK_RelStress": self.selected_stress_pks,
                "removed": 0
            })
            result_existing = self.cur.execute(sql).fetchall()
            existing = set(result["FailureMode"] for result in result_existing)
            return self.failure_mode_list - existing
        return {None}

    @property
    def failure_mode_list(self):
        if self.cur:
            sql = "SELECT FailureMode FROM FailureMode_T  " + \
                  self.sql_filter_str(({
                      "FailureGroup": self.filter_set.get("failure_group"),
                      "removed": 0
                  }))
            results = self.cur.execute(sql).fetchall()
            all_failure_mode = set(result["FailureMode"] for result in results)
            return all_failure_mode
        else:
            return {None}

    @property
    def rel_log_table_view_data(self):
        condition = {"RelLog_T.WIP": self.filter_set.get("wip"),
                     "RelLog_T.SerialNumber": self.filter_set.get("serial_number"),
                     "Config_FK": self.selected_config_pks,
                     "FK_RelStress": self.selected_stress_pks,
                     "Station": self.display_setting.get("station_filter"),
                     "RelLog_T.removed": 0
                     }
        if self.cur:
            sql = f'SELECT RelLog_T.PK,Config_T.Config, RelLog_T.WIP,RelLog_T.SerialNumber,' \
                  f'Station,StartTime,EndTime, RelStress_T.RelStress, ' \
                  f'RelStress_T.RelCheckpoint,RelLog_T.Notes ' \
                  f'FROM RelLog_T ' \
                  f'  inner Join RelStress_T ON RelLog_T.FK_RelStress = RelStress_T.PK ' + \
                  f'  inner Join Config_SN_T ON RelLog_T.SerialNumber = Config_SN_T.SerialNumber ' + \
                  f'  inner Join Config_T ON Config_SN_T.Config_FK = Config_T.PK ' + \
                  self.sql_filter_str(condition) + \
                  ' ORDER BY RelLog_T.ModiTimestamp DESC LIMIT 200'
            results = self.cur.execute(sql).fetchall()

            if results is None:
                return [dict()]
            else:
                return [dict(result) for result in results]
        else:
            return [dict()]

    @property
    def all_station_rel_log_table_view_data(self):
        condition = {"RelLog_T.WIP": self.filter_set.get("wip"),
                     "RelLog_T.SerialNumber": self.filter_set.get("serial_number"),
                     "Config_FK": self.selected_config_pks,
                     "FK_RelStress": self.selected_stress_pks,
                     "RelLog_T.removed": 0
                     }
        if self.cur:
            sql = f'SELECT RelLog_T.PK,Config_T.Config, RelLog_T.WIP,RelLog_T.SerialNumber,' \
                  f'Station,StartTime,EndTime, RelStress_T.RelStress, ' \
                  f'RelStress_T.RelCheckpoint ' \
                  f'FROM RelLog_T ' \
                  f'  inner Join RelStress_T ON RelLog_T.FK_RelStress = RelStress_T.PK ' + \
                  f'  inner Join Config_SN_T ON RelLog_T.SerialNumber = Config_SN_T.SerialNumber ' + \
                  f'  inner Join Config_T ON Config_SN_T.Config_FK = Config_T.PK ' + \
                  self.sql_filter_str(condition) + \
                  ' ORDER BY RelLog_T.ModiTimestamp DESC LIMIT 200'
            results = self.cur.execute(sql).fetchall()
            if results is None:
                return [dict()]
            else:
                return [dict(result) for result in results]
        else:
            return [dict()]

    @property
    def fa_log_table_view_data(self):
        condition = {
            "FALog_T.WIP": self.filter_set.get("wip"),
            "FALog_T.SerialNumber": self.filter_set.get("serial_number"),
            "Config_FK": self.selected_config_pks,
            "FailureMode": self.filter_set.get("failure_mode"),
            "FK_RelStress": self.selected_stress_pks,
            "Station": self.display_setting.get("station_filter"),
            "FALog_T.removed": 0
        }
        if self.cur:
            sql = f'SELECT FALog_T.PK,Config_T.Config,FALog_T.SerialNumber,' \
                  f'FALog_T.Station,FALog_T.StartTime,RelStress_T.RelStress,' \
                  f' FALog_T.FailureMode,FALog_T.FailureGroup,' \
                  f'RelStress_T.RelCheckpoint, FALog_T.FA_Details' \
                  f' FROM FALog_T ' \
                  f' inner Join RelStress_T ON FALog_T.FK_RelStress = RelStress_T.PK ' + \
                  f' inner Join Config_SN_T ON FALog_T.SerialNumber = Config_SN_T.SerialNumber ' + \
                  f' inner Join Config_T ON Config_SN_T.Config_FK = Config_T.PK ' + \
                  self.sql_filter_str(condition) + \
                  '   LIMIT 200'
            results = self.cur.execute(sql).fetchall()
            if results is None:
                return [dict()]
            else:
                return [dict(result) for result in results]
        else:
            return [dict()]

    @property
    def tagger_log_table_view_data(self):
        condition = {
            "Tagger_Log_T.WIP": self.filter_set.get("wip"),
            "Tagger_Log_T.SerialNumber": self.filter_set.get("serial_number"),
            "FK_Config": self.selected_config_pks,
            "FK_RelStress": self.selected_stress_pks,
            "Station": self.display_setting.get("station_filter"),
            "Tagger_Log_T.removed": 0,
        }
        if self.cur:
            sql = f'SELECT Tagger_Log_T.PK,Tagger_Log_T.WIP, Config_T.Config,Tagger_Log_T.SerialNumber,' \
                  f'Tagger_Log_T.Station,Tagger_Log_T.StartTime,RelStress_T.RelStress,' \
                  f' Tagger_Log_T.EndTime,Tagger_Log_T.FolderGroup,Tagger_Log_T.Notes,' \
                  f'RelStress_T.RelCheckpoint' \
                  f' FROM Tagger_Log_T ' \
                  f' inner Join RelStress_T ON Tagger_Log_T.FK_RelStress = RelStress_T.PK ' + \
                  f' inner Join Config_T ON Tagger_Log_T.FK_Config = Config_T.PK ' + \
                  self.sql_filter_str(condition) + \
                  '   LIMIT 200'
            results = self.cur.execute(sql).fetchall()
            if results is None:
                return [dict()]
            else:
                return [dict(result) for result in results]
        else:
            return [dict()]

    @property
    def all_station_latest_sn_history(self):
        condition = {
            "RelLog_T.WIP": self.filter_set.get("wip"),
            "RelLog_T.SerialNumber": self.filter_set.get("serial_number"),
            "FK_RelStress": self.selected_stress_pks,
            "RelLog_T.removed": 0
        }
        condition2 = {
            "Config_SN_T.Config_FK": self.selected_config_pks,
        }
        if self.cur:
            sql = "SELECT RelLog_T.PK,RelLog_T.SerialNumber,RelLog_T.WIP,Config_T.Config, RelLog_T.StartTime, " \
                  " RelLog_T.EndTime, RelLog_T.Notes, RelStress_T.RelStress,RelStress_T.RelCheckpoint " \
                  " from RelLog_T inner join (SELECT Max(StartTimestamp) as " \
                  " StartTimestamp,SerialNumber from RelLog_T  " \
                  + self.sql_filter_str(condition) + \
                  " GROUP BY SerialNumber) as A " \
                  " on A.StartTimestamp = RelLog_T.StartTimestamp and A.SerialNumber = RelLog_T.SerialNumber" \
                  " inner join Config_SN_T ON " \
                  " Config_SN_T.SerialNumber = RelLog_T.SerialNumber " \
                  " inner join Config_T ON Config_T.PK = Config_SN_T.Config_FK " \
                  " inner join RelStress_T ON RelStress_T.PK = RelLog_T.FK_RelStress " \
                  + self.sql_filter_str(condition2) + \
                  ' ORDER BY RelLog_T.ModiTimestamp DESC LIMIT 200'

            results = self.cur.execute(sql).fetchall()
            if results is None:
                return [dict()]
            else:
                return [dict(result) for result in results]
        else:
            return [dict()]

    @property
    def latest_sn_history(self):

        condition = {
            "RelLog_T.WIP": self.filter_set.get("wip"),
            "RelLog_T.SerialNumber": self.filter_set.get("serial_number"),
            "FK_RelStress": self.selected_stress_pks,
            "RelLog_T.removed": 0,
            "Station": self.display_setting.get("station_filter"),
        }
        condition2 = {
            "Config_SN_T.Config_FK": self.selected_config_pks,
        }
        if self.cur:
            sql = "SELECT RelLog_T.PK,RelLog_T.SerialNumber,RelLog_T.WIP,Config_T.Config, RelLog_T.StartTime, " \
                  " RelLog_T.EndTime, RelLog_T.Notes, RelStress_T.RelStress,RelStress_T.RelCheckpoint " \
                  " from RelLog_T inner join (SELECT Max(StartTimestamp) as " \
                  " StartTimestamp,SerialNumber from RelLog_T  " \
                  + self.sql_filter_str(condition) + \
                  " GROUP BY SerialNumber LIMIT 200) as A " \
                  " on A.StartTimestamp = RelLog_T.StartTimestamp and A.SerialNumber = RelLog_T.SerialNumber" \
                  " inner join Config_SN_T ON " \
                  " Config_SN_T.SerialNumber = RelLog_T.SerialNumber " \
                  " inner join Config_T ON Config_T.PK = Config_SN_T.Config_FK " \
                  " inner join RelStress_T ON RelStress_T.PK = RelLog_T.FK_RelStress " \
                  + self.sql_filter_str(condition2) + \
                  ' ORDER BY RelLog_T.ModiTimestamp DESC LIMIT 200 '
            results = self.cur.execute(sql).fetchall()
            if results is None:
                return [dict()]
            else:
                return [dict(result) for result in results]
        else:
            return [dict()]

    @property
    def completed_rel_summary_data(self):
        condition = {
            "FK_RelStress": self.selected_stress_pks,
            "RelLog_T.removed": 0,
            "RelLog_T.EndTimestamp": "not none",
            "Config_SN_T.Config_FK": self.selected_config_pks,
        }
        sql = "SELECT  COUNT (DISTINCT RelLog_T.SerialNumber) as SN_Count, " \
              "RelLog_T.FK_RelStress, Config_SN_T.Config_FK" \
              " from RelLog_T" \
              " inner join Config_SN_T on Config_SN_T.SerialNumber = RelLog_T.SerialNumber" \
              + self.sql_filter_str(condition) + \
              " Group by FK_RelStress,Config_SN_T.Config_FK "
        result = self.cur.execute(sql).fetchall()
        if result is None:
            return [dict()]
        else:
            return [dict(result) for result in result]

    @property
    def ongoing_rel_summary_data(self):
        """
        aggregation over relstress and config, on-going unit only
        :return: a list of dict, key: SN_Count, FK_RelStress, Config_FK
        """
        condition = {
            "FK_RelStress": self.selected_stress_pks,
            "RelLog_T.removed": 0,
            "RelLog_T.EndTimestamp": "none",
            "Config_SN_T.Config_FK": self.selected_config_pks,
        }
        sql = " SELECT  COUNT (DISTINCT RelLog_T.SerialNumber) as SN_Count, " \
              " RelLog_T.FK_RelStress, Config_SN_T.Config_FK" \
              " from RelLog_T" \
              " inner join Config_SN_T on Config_SN_T.SerialNumber = RelLog_T.SerialNumber" \
              + self.sql_filter_str(condition) + \
              " Group by FK_RelStress,Config_SN_T.Config_FK "
        result = self.cur.execute(sql).fetchall()
        if result is None:
            return [dict()]
        else:
            return [dict(result) for result in result]

    @property
    def fa_summary_data(self):
        condition = {
            "FALog_T.FK_RelStress": self.selected_stress_pks,
            "FALog_T.removed": 0,
            "Config_SN_T.Config_FK": self.selected_config_pks,
            "FailureMode": self.filter_set.get("failure_mode")
        }
        sql = " SELECT  COUNT (DISTINCT FALog_T.SerialNumber) as SN_Count," \
              " FALog_T.FK_RelStress, Config_SN_T.Config_FK, " \
              " FailureMode from FALog_T" \
              " inner join Config_SN_T on Config_SN_T.SerialNumber = FALog_T.SerialNumber" \
              + self.sql_filter_str(condition) + \
              " Group by FK_RelStress,Config_SN_T.Config_FK"
        result = self.cur.execute(sql).fetchall()
        if result is None:
            return [dict()]
        else:
            return [dict(result) for result in result]

    @property
    def data_tag(self):
        """
        0: foldergroup, 1: program, 2: build, 3.config, 4.serialnumber, 5. relstress, 6. relcheckpoint.
        :return:
        """
        file_creation_time = self.filter_set.get("file_creation_time")
        if isinstance(file_creation_time, float):
            sql = " SELECT Tagger_Log_T.FolderGroup, Config_T.Program, Config_T.Build, Config_T.Config," \
                  " Tagger_Log_T. SerialNumber, RelStress_T.RelStress, RelStress_T.RelCheckpoint FROM Tagger_Log_T" \
                  " Inner Join Config_T ON Config_T.PK = Tagger_Log_T.FK_Config" \
                  " Inner Join RelStress_T ON RelStress_T.PK = Tagger_Log_T.FK_RelStress" \
                  " WHERE StartTimestamp < ? and EndTimestamp > ?" \
                  " AND Tagger_Log_T.removed = 0 AND Tagger_Log_T.Station = ?"
            results = self.cur.execute(sql, (file_creation_time, file_creation_time, self.station)).fetchall()
            if results:
                if len(results) > 1:
                    print("there is ambiguity, no tag")
                    return None
                else:
                    result = results[0]
                    a = (result["FolderGroup"], result["Program"],
                         result["Build"], result["Config"], result["SerialNumber"],
                         result["RelStress"], result["RelCheckpoint"])
                    return a

    @property
    def on_going_wip(self):
        sql = " SELECT WIP, min(StartTimestamp) as Start, " \
              " EndTimestamp is Null as On_going, COUNT(DISTINCT SerialNumber) as Count from RelLog_T" \
              " WHERE removed = 0 " \
              " GROUP By WIP, EndTimestamp is Null "
        results = self.cur.execute(sql).fetchall()
        if results:
            return [dict(result) for result in results]
        else:
            return [dict()]

    @property
    def program_list(self):
        if self.cur:
            sql = "SELECT Distinct Program FROM Config_T "
            results = self.cur.execute(sql).fetchall()
            return set(result["Program"] for result in results)
        return {None}

    @property
    def build_list(self):
        if self.cur:
            sql = "SELECT Distinct Build FROM Config_T "
            results = self.cur.execute(sql).fetchall()
            return set(result["Build"] for result in results)
        else:
            return {None}

    @property
    def stress_list(self):
        if self.cur:
            sql = "SELECT Distinct RelStress FROM RelStress_T WHERE removed = 0"
            results = self.cur.execute(sql).fetchall()
            return set(result["RelStress"] for result in results)
        else:
            return {None}

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
        result = self.cur.execute(f'SELECT WIP FROM WIP_Status_T WHERE WIP =? LIMIT 1', (wip,)).fetchone()
        return result is not None
        # return wip.upper() in self.cache_wip_table.records.keys()

    def config_exist(self, idx):
        """
        :param idx: "int"
        :return: bool
        """
        result = self.con.execute(f'SELECT PK FROM Config_T WHERE PK =?', (idx,)).fetchone()
        return result is not None

    def stress_exist(self, idx):
        """
        :param idx: "int"
        :return: bool
        """
        result = self.con.execute(f'SELECT PK FROM RelStress_T WHERE PK =?', (idx,)).fetchone()
        return result is not None

    def sync_rel_log_table(self, golden_db_address: str = None, cutoff_time: float = 0.0):
        """
        this will upload data from a specific station to gold and download from gold data that doesn't below to
        this station
        :param cutoff_time: cut off time should be saved as user setting, if get nonthing form user setting,
        then use default 0
        :param golden_db_address: database address
        :return: bool
        """
        if not isinstance(golden_db_address, str):
            return False
        if not isinstance(self.station, str):
            return False
        self.cur.execute("ATTACH ? AS GOLD ", (golden_db_address,))
        sql = f'INSERT OR REPLACE INTO GOLD.RelLog_T SELECT * FROM main.RelLog_T WHERE removed = 0 and Station = ?'
        sql2 = f'INSERT OR REPLACE INTO GOLD.Config_SN_T ' \
               f'SELECT Config_SN_T.* FROM main.Config_SN_T INNER JOIN main.RelLog_T ' \
               f'ON main.Config_SN_T.SerialNumber = main.RelLog_T.SerialNumber ' \
               f'WHERE RelLog_T.removed = 0 and Station = ?'
        sql3 = f'INSERT OR REPLACE INTO main.RelLog_T SELECT * FROM GOLD.RelLog_T ' \
               f'WHERE GOLD.RelLog_T.removed = 0 and GOLD.RelLog_T.Station <> ?'
        sql4 = f'delete from gold.RelLog_T WHERE PK in (SELECT PK FROM main.RelLog_T WHERE main.RelLog_T.removed = 1)'
        sql5 = f'delete from main.RelLog_T WHERE PK in (SELECT PK FROM gold.RelLog_T WHERE gold.RelLog_T.removed = 1)'
        self.cur.execute(sql5)
        self.cur.execute(sql4)
        self.cur.execute(sql2, (self.station,))
        self.cur.execute(sql, (self.station,))
        self.cur.execute(sql3, (self.station,))

        self.con.commit()
        self.cur.execute("DETACH DATABASE ? ", ("GOLD",))

    def sync_fa_log_table(self, golden_db_address: str = None, cutoff_time: float = 0.0):
        """
        this will upload data from a specific station to gold and download from gold data that doesn't below to
        this station
        :param cutoff_time: cut off time should be saved as user setting, if get nonthing form user setting,
        then use default 0
        :param golden_db_address: database address
        :return: bool
        """
        if not isinstance(golden_db_address, str):
            return False
        if not isinstance(self.station, str):
            return False
        self.cur.execute("ATTACH ? AS GOLD ", (golden_db_address,))
        sql = f'INSERT OR REPLACE INTO GOLD.FALog_T SELECT * FROM main.FALog_T WHERE removed = 0 and Station = ?'
        sql3 = f'INSERT OR REPLACE INTO main.FALog_T ' \
               f'SELECT * FROM GOLD.FALog_T WHERE GOLD.FALog_T.removed = 0 and GOLD.FALog_T.Station <> ?'
        sql4 = f'delete from GOLD.FALog_T WHERE PK in (SELECT PK FROM main.FALog_T WHERE main.FALog_T.removed = 1)'
        sql5 = f'delete from main.FALog_T WHERE PK in (SELECT PK FROM GOLD.FALog_T WHERE GOLD.FALog_T.removed = 1)'
        self.cur.execute(sql5)
        self.cur.execute(sql4)
        self.cur.execute(sql, (self.station,))
        self.cur.execute(sql3, (self.station,))
        self.con.commit()
        self.cur.execute("DETACH DATABASE ? ", ("GOLD",))

    def sync_tagger_log_table(self, golden_db_address: str = None, cutoff_time: float = 0.0):
        """
        this will upload data from a specific station to gold and download from gold data that doesn't below to
        this station
        :param cutoff_time: cut off time should be saved as user setting, if get nonthing form user setting,
        then use default 0
        :param golden_db_address: database address
        :return: bool
        """
        if not isinstance(golden_db_address, str):
            return False
        if not isinstance(self.station, str):
            return False
        self.cur.execute("ATTACH ? AS GOLD ", (golden_db_address,))
        sql = f'INSERT OR REPLACE INTO GOLD.Tagger_Log_T SELECT * FROM main.Tagger_Log_T' \
              f' WHERE removed = 0 and Station = ?'
        sql3 = f'INSERT OR REPLACE INTO main.Tagger_Log_T ' \
               f'SELECT * FROM GOLD.Tagger_Log_T WHERE GOLD.Tagger_Log_T.removed = 0 and GOLD.Tagger_Log_T.Station <> ?'
        sql4 = f'delete from GOLD.Tagger_Log_T WHERE PK in ' \
               f'(SELECT PK FROM main.Tagger_Log_T WHERE main.Tagger_Log_T.removed = 1)'
        sql5 = f'delete from main.Tagger_Log_T WHERE PK in ' \
               f' (SELECT PK FROM GOLD.Tagger_Log_T WHERE GOLD.Tagger_Log_T.removed = 1)'
        self.cur.execute(sql5)
        self.cur.execute(sql4)
        self.cur.execute(sql, (self.station,))
        self.cur.execute(sql3, (self.station,))
        self.con.commit()
        self.cur.execute("DETACH DATABASE ? ", ("GOLD",))

    def sync_reference_tables(self, golden_db_address: str = None, cutoff_time: float = 0.0):
        if not isinstance(golden_db_address, str):
            return False
        self.cur.execute("ATTACH ? AS GOLD ", (golden_db_address,))
        sql = f'INSERT OR REPLACE INTO GOLD.RelStress_T SELECT * FROM main.RelStress_T WHERE removed = 0'
        sql3 = f'INSERT OR REPLACE INTO main.RelStress_T ' \
               f'SELECT * FROM GOLD.RelStress_T WHERE GOLD.RelStress_T.removed = 0'
        self.cur.execute(sql)
        self.cur.execute(sql3)
        self.con.commit()
        sql = f'INSERT OR REPLACE INTO GOLD.Config_T SELECT * FROM main.Config_T WHERE removed = 0'
        sql3 = f'INSERT OR REPLACE INTO main.Config_T SELECT * FROM GOLD.Config_T WHERE GOLD.Config_T.removed = 0'
        self.cur.execute(sql)
        self.cur.execute(sql3)
        self.con.commit()
        sql = f'INSERT OR REPLACE INTO GOLD.FailureMode_T SELECT * FROM main.FailureMode_T WHERE removed = 0'
        sql3 = f'INSERT OR REPLACE INTO main.FailureMode_T ' \
               f'SELECT * FROM GOLD.FailureMode_T WHERE GOLD.FailureMode_T.removed = 0'
        self.cur.execute(sql)
        self.cur.execute(sql3)
        self.con.commit()
        self.cur.execute("DETACH DATABASE ? ", ("GOLD",))

    def insert_to_failure_log_table(self):
        current_time = dt.datetime.now().timestamp()
        time_str = dt.datetime.now().strftime('%m-%d %H:%M:%S')
        if isinstance(self.filter_set.get("failure_mode"), list):
            for failure_mode in self.filter_set.get("failure_mode"):
                uuid_str = str(uuid.uuid1())
                log = {
                    "PK": uuid_str,
                    "FK_RelStress": self.selected_stress_pks.pop(),
                    "Station": self.filter_set.get('station'),
                    "SerialNumber": self.filter_set.get("serial_number"),
                    "FailureGroup": self.filter_set.get("failure_group"),
                    "FailureMode": failure_mode,
                    "StartTimestamp": current_time,
                    "StartTime": time_str,
                    "WIP": SnModel(self.filter_set.get("serial_number"), self).wip,
                    "removed": 0
                }
                if self.__insert_to_table__("FALog_T", **log):
                    self.con.commit()
                    print(f"added {failure_mode} to {self.filter_set.get('serial_number')}")

    def delete_from_failure_log_table(self):
        count = 0
        for pk in self.filter_set.get("selected_pks"):
            if self.__delete_from_table__("FALog_T", {"PK": pk}):
                self.con.commit()
                count += 1
            else:
                self.con.rollback()
                print("error, delete is not completed")
        print(f"{count} rows are deleted from failure_log")

    def update_failure_log_table(self, **log):
        if isinstance(self.filter_set.get("selected_pks"), list):
            condition = {
                "PK": self.filter_set.get("selected_pks")
            }
            self.__update_to_table__("FALog_T", condition=condition, **log)
        self.con.commit()

    def insert_to_failure_mode_table(self, failure_mode: str = None):
        # current_time = dt.datetime.now().timestamp()
        # time_str = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(failure_mode, str):
            log = {
                "PK": str(uuid.uuid1()),
                "FailureGroup": "Default",
                "FailureMode": failure_mode,
                "removed": 0
            }
            if self.__insert_to_table__("FailureMode_T", **log):
                self.con.commit()
                print(f'{failure_mode} created in Default group, move to other group as needed')

    def update_failure_mode_table(self, group_name: str = None):
        # this will not only update in failure_mode table but also update FA_Log
        if isinstance(group_name, str):
            condition = {
                "FailureMode": self.filter_set.get("failure_mode")
            }
            log = {
                "FailureGroup": group_name
            }
            if self.__update_to_table__("FALog_T", condition=condition, **log) and \
                    self.__update_to_table__("FailureMode_T", condition=condition, **log):
                self.con.commit()

    def delete_from_failure_mode_table(self):
        condition = {
            "FailureMode": self.filter_set.get("failure_mode")
        }
        if self.__delete_from_table__("FailureMode_T", condition):
            self.con.commit()
            print(f'{self.filter_set.get("failure_mode")} get deleted')
        else:
            self.con.rollback()

    def insert_new_to_rel_log_table(self):
        current_time = dt.datetime.now().timestamp()
        time_str = dt.datetime.now().strftime('%m-%d %H:%M:%S')
        count = 0
        if isinstance(self.filter_set.get("serial_number_list"), list):
            for sn in self.filter_set.get("serial_number_list"):
                if not self.sn_exist(sn):
                    uuid_str = str(uuid.uuid1())
                    if self.selected_stress_pks:
                        if len(self.selected_stress_pks) == 0:
                            return False
                        stress_fk = self.selected_stress_pks.pop()
                        log = {
                            "PK": uuid_str,
                            "FK_RelStress": stress_fk,
                            "Stress_FK": stress_fk,
                            "Config_FK": self.selected_config_pks.pop(),
                            "DateAdded": current_time,
                            "ModiTimestamp": current_time,
                            "Station": self.filter_set.get('station'),
                            "SerialNumber": sn,
                            "StartTimestamp": current_time,
                            "StartTime": time_str,
                            "EndTimestamp": None,
                            "EndTime": None,
                            "WIP": self.filter_set.get("wip"),
                            "removed": 0,
                            "Notes": self.filter_set.get("note")
                        }
                        if self.__insert_to_table__("Config_SN_T", **log):
                            log.update({"PK": str(uuid.uuid1())})
                            if self.__insert_to_table__("RelLog_T", **log):
                                self.con.commit()
                                count = count + 1
                            else:
                                self.con.rollback()
                        else:
                            self.con.rollback()
            print(f'{count} units are added to system')

    def checkin_to_new_checkpoint_rellog_table(self):
        current_time = dt.datetime.now().timestamp()
        time_str = dt.datetime.now().strftime('%m-%d %H:%M:%S')
        new_stress_pk = self.selected_stress_pks
        count = 0
        if new_stress_pk:
            stress_pk = self.selected_stress_pks.pop()
        else:
            return
        for pk in self.filter_set.get("selected_pks"):
            result = self.cur.execute("SELECT * FROM RelLog_T WHERE PK = ?", (pk,)).fetchone()
            uuid_str = str(uuid.uuid1())
            log = {
                "PK": uuid_str,
                "FK_RelStress": stress_pk,
                "Stress_FK": stress_pk,
                "DateAdded": current_time,
                "Station": self.filter_set.get('station'),
                "SerialNumber": result["SerialNumber"],
                "StartTimestamp": current_time,
                "StartTime": time_str,
                "EndTimestamp": None,
                "EndTime": None,
                "WIP": result["WIP"],
                "removed": 0,
                "Notes": self.filter_set.get("note"),
                "ModiTimestamp": current_time
            }
            if self.__insert_to_table__("RelLog_T", **log):
                self.con.commit()
                count = count + 1
            else:
                self.con.rollback()
                print("error checkin ?to next checkpoint, no insert".format(result["SerialNumber"]))
        print(f'{count} units checkin to {str(StressModel(stress_pk, self))}')

    def checkout_current_checkpoint_rellog_table(self):
        current_time = dt.datetime.now().timestamp()
        time_str = dt.datetime.now().strftime('%m-%d %H:%M:%S')
        if isinstance(self.filter_set.get("selected_pks"), list):
            condition = {
                "PK": self.filter_set.get("selected_pks")
            }
            log = {
                "EndTimestamp": current_time,
                "EndTime": time_str,
                "ModiTimestamp": current_time
            }
            if self.__update_to_table__("RelLog_T", condition=condition, **log):
                self.con.commit()
                print(f'{self.cur.rowcount} rows checkout from current checkpoint')
            else:
                self.con.rollback()

    def update_current_row_rellog_table(self):
        """
        this will update current row only, except for SN if it's updated, all the same SN got updated.
        sn could belong to different wip at different time, if it's underFA, will update WIP to "FA"
        there is a bug (rare situation) that when you update a previous log, this will reset wip.
        """
        current_time = dt.datetime.now().timestamp()
        stress_pk = self.selected_stress_pks.pop()
        config_pk = self.selected_config_pks.pop()
        for pk in self.filter_set.get("selected_pks"):
            result = self.cur.execute("SELECT * FROM RelLog_T WHERE PK = ?", (pk,)).fetchone()
            # date_added_to_config_sn_t = self.cur.execute("SELECT DateAdded FROM Config_SN_T WHERE SerialNumber = ?",
            #                                              (result["SerialNumber"],)).fetchone()["DateAdded"]
            condition1 = {
                "PK": pk,
            }
            log1 = {
                "FK_RelStress": stress_pk,
                "WIP": self.filter_set.get("wip"),
                "notes": self.filter_set.get("note"),
                "ModiTimestamp": current_time
            }
            condition2 = {
                "SerialNumber": result["SerialNumber"],
            }
            log2 = {
                "Config_FK": config_pk,
                "SerialNumber": self.filter_set.get("serial_number"),
                "DateChanged": current_time,  # depricated
                # "WIP": wip,
            }
            if self.__update_to_table__("Config_SN_T", condition2, **log2):
                if self.__update_to_table__("RelLog_T", condition1, **log1):
                    self.con.commit()
                    print(f"{self.cur.rowcount} row in rel log updated")
                else:
                    self.con.rollback()
            else:
                self.con.rollback()
                print("error updating ?, no insert".format(result["SerialNumber"]))

    def assign_wip_row_rellog_table(self, wip: str = None):
        current_time = dt.datetime.now().timestamp()
        count = 0
        if isinstance(self.filter_set.get("serial_number_list"), list):
            for sn in self.filter_set.get("serial_number_list"):
                if self.sn_exist(sn):
                    log = {
                        "WIP": wip,
                        "ModiTimestamp": current_time
                    }
                    # condition = {
                    #     "SerialNumber": sn
                    # }
                    # if self.__update_to_table__("Config_SN_T", condition, **log):
                    condition = {
                        "PK": SnModel(sn, self).last_rel_log_row_pk
                    }
                    if self.__update_to_table__("RelLog_T", condition, **log):
                        self.con.commit()
                        count = count + 1
                    else:
                        self.con.rollback()
        print(f"{count} units added to WIP: {wip}, now you can start tracking them as a group")

    def delete_from_rellog_table(self):
        count = 0
        for pk in self.filter_set.get("selected_pks"):
            if self.__delete_from_table__("RelLog_T", {"PK": pk}):
                self.con.commit()
                count += 1
            else:
                self.con.rollback()
        print(f'{count} rows deleted from RelLog')

    def delete_from_tagger_log_table(self):
        count = 0
        for pk in self.filter_set.get("selected_pks"):
            if self.__delete_from_table__("Tagger_Log_T", {"PK": pk}):
                self.con.commit()
                count += 1
            else:
                self.con.rollback()
        print(f'{count} rows deleted from TaggerLog')

    def insert_to_stress_table(self, rel_checkpoint: str = None):
        if isinstance(rel_checkpoint, str):
            log = {
                "PK": str(uuid.uuid1()),
                "RelStress": self.filter_set.get("stress"),
                "RelCheckpoint": rel_checkpoint,
                "removed": 0
            }
            if self.__insert_to_table__("RelStress_T", **log):
                self.con.commit()
                print(f'{rel_checkpoint} added to {self.filter_set.get("stress")}')

    def update_stress_table(self, stress_name, checkpoints: list = None):
        # this will not only update in failure_mode table but also update FA_Log
        if isinstance(stress_name, str):
            condition = {
                "RelStress": self.filter_set.get("stress"),
                "RelCheckpoint": checkpoints
            }
            log = {
                "RelStress": stress_name
            }
            if self.__update_to_table__("RelStress_T", condition=condition, **log):
                self.con.commit()

    def delete_from_stress_table(self, checkpoints: list = None):
        condition = {
            "RelStress": self.filter_set.get("stress"),
            "RelCheckpoint": checkpoints
        }
        if self.__delete_from_table__("RelStress_T", condition):
            self.con.commit()
            print(f'{checkpoints} deleted from {self.filter_set.get("stress")}')
        else:
            self.con.rollback()

    def insert_to_config_table(self, config_name: str = None):
        if isinstance(config_name, str):
            log = {
                "PK": str(uuid.uuid1()),
                "Program": self.filter_set.get("program"),
                "Build": self.filter_set.get("build"),
                "Config": config_name,
                "removed": 0
            }
            if self.__insert_to_table__("Config_T", **log):
                self.con.commit()
                print(f'{config_name} added to {self.filter_set.get("program")} {self.filter_set.get("build")}')

    def update_config_table(self, config_name: str = None):
        # this will not only update in failure_mode table but also update FA_Log
        if isinstance(config_name, str):
            condition = {
                "Program": self.filter_set.get("program"),
                "Build": self.filter_set.get("build"),
                "Config": self.filter_set.get("config")
            }
            log = {
                "Config": config_name
            }
            if self.__update_to_table__("Config_T", condition=condition, **log):
                self.con.commit()

    def start_timer_data_table(self):
        current_time = dt.datetime.now().timestamp()
        time_str = dt.datetime.now().strftime('%m-%d %H:%M:%S')
        uuid_str = str(uuid.uuid1())
        log = {
            "PK": uuid_str,
            "FK_RelStress": self.selected_stress_pks.pop(),
            "FK_Config": self.selected_config_pks.pop(),
            "Station": self.filter_set.get('station'),
            "SerialNumber": self.filter_set.get("serial_number"),
            "StartTimestamp": current_time,
            "StartTime": time_str,
            "WIP": self.filter_set.get("wip"),
            "removed": 0
        }
        if self.__insert_to_table__("Tagger_Log_T", **log):
            self.con.commit()
            print(f'timer started for {self.filter_set.get("serial_number")}, '
                  f'you may start parametric test, please make sure parametric raw data is generated before end timer')

    def end_timer_data_table(self, pk: str = None):
        if pk:
            current_time = dt.datetime.now().timestamp()
            time_str = dt.datetime.now().strftime('%m-%d %H:%M:%S')
            result = self.cur.execute("SELECT EndTimestamp from Tagger_Log_T WHERE PK = ? ", (pk,)).fetchone()
            if result["EndTimestamp"] is None:
                log = {
                    "EndTimestamp": current_time,
                    "EndTime": time_str,
                    "removed": 0
                }
                condition = {
                    "PK": pk
                }
                if self.__update_to_table__("Tagger_Log_T", condition, **log):
                    self.con.commit()
                    print(f"timer stopped. transfer data to 'Input_folder' to do Rel event tagging.")
                else:
                    self.con.rollback()

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
        for col in self.__get_col_names__(tablename):
            values.append(log.get(col))
            col_to_add.append(col)
        cols_str = ",".join(col_to_add)
        values_tup = tuple(values)
        ques_mark = self.__construct_question_mark__(tablename)
        sql = "INSERT OR REPLACE INTO " + tablename + " (" + cols_str + ") VALUES " + ques_mark
        try:
            self.cur.execute(sql, values_tup)
        except sqlite3.Error as e:
            print(e)
            return False
        return True

    def __update_to_table__(self, tablename: str, condition: dict, **log):
        # when value is none, it will not get updated, set to "" if need to update
        set_statement = []
        value_list = []

        for k in condition.keys():
            if k not in self.__get_col_names__(tablename):
                condition.update({k: None})
        condition_str = self.sql_filter_str(condition, strict=True)
        for key, value in log.items():
            if key in self.__get_col_names__(tablename):
                if value is not None:
                    s = f" {key} = ? "
                    set_statement.append(s)
                    value_list.append(value)
        value_list = tuple(value_list)
        if len(set_statement) == 0:
            return True
        set_statements = " SET " + ",".join(set_statement)
        sql = "UPDATE " + tablename + set_statements + condition_str
        # print(sql, value_list)
        try:
            self.cur.execute(sql, value_list)
        except sqlite3.Error as e:
            print(e)
            return False
        return True

    def __delete_from_table__(self, tablename: str, condition: dict):
        log = {
            "removed": 1
        }

        if None in condition.values():
            return False

        return self.__update_to_table__(tablename, condition, **log)


class ConfigModel:
    def __init__(self, idx: int = None, database: DBsqlite = None):
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
        sql = f'SELECT Config, Program, Build From Config_T WHERE PK = ?'
        if self.database:
            if self.database.config_exist(idx):
                result = self.database.cur.execute(sql, (idx,)).fetchone()
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
    def __init__(self, idx: str = None, database: DBsqlite = None):
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
        sql = f'SELECT RelStress, RelCheckpoint From RelStress_T WHERE PK = ?'
        if self.database:
            if self.database.stress_exist(idx):
                result = self.database.cur.execute(sql, (idx,)).fetchone()
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
    def __init__(self, sn: str = None, database: DBsqlite = None):
        self.database = database
        self.serial_number = sn

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, sn):
        self._serial_number = None
        self._config = ConfigModel(None, None)
        self._wip = None
        if not (sn is None or sn == ""):
            if self.database:
                if self.database.sn_exist(sn):
                    sql = f'SELECT SerialNumber,Config_FK, ' \
                          f'DateAdded From Config_SN_T WHERE SerialNumber like "{sn}%" '
                    result = self.database.cur.execute(sql).fetchone()
                    self._serial_number = result["SerialNumber"]
                    self._config = ConfigModel(result["Config_FK"], self.database)

    @property
    def config(self):
        return self._config

    @property
    def wip(self):
        return self._wip

    @property
    def last_rel_log_row_pk(self):
        sql = "SELECT RelLog_T.PK" \
              " from RelLog_T inner join (SELECT Max(StartTimestamp) as " \
              " StartTimestamp, SerialNumber from RelLog_T  " \
              " WHERE removed = 0 and SerialNumber = ?" \
              " GROUP BY SerialNumber LIMIT 1) as A " \
              " on A.StartTimestamp = RelLog_T.StartTimestamp and A.SerialNumber = RelLog_T.SerialNumber" \
              " WHERE RelLog_T.SerialNumber = ? LIMIT 1"
        result = self.database.cur.execute(sql, (self.serial_number, self.serial_number)).fetchone()
        if result:
            return result["PK"]
        else:
            return None

    def is_latest_row(self, pk):
        if isinstance(pk, str):
            return pk == self.last_rel_log_row_pk
        else:
            return False


class StatusSummary:
    def __init__(self, db: DBsqlite = None):
        self.on_going = db.ongoing_rel_summary_data
        self.completed = db.completed_rel_summary_data
        self.failures = db.fa_summary_data
        self.database = db
        if db.selected_config_pks:
            self.configs = db.selected_config_pks
        else:
            self.configs = db.all_config_pks
        if db.selected_stress_pks:
            self.stress = db.selected_stress_pks
        else:
            self.stress = db.all_stress_pks
        self.stress_obj_list = self.get_stress_obj_list()

    def get_config_obj_list(self):
        result = [ConfigModel(pk, self.database) for pk in self.configs]
        result.sort(key=lambda x: x.config_name)
        return result

    def get_stress_obj_list(self):
        result = [StressModel(pk, self.database) for pk in self.stress]
        result.sort(key=lambda x: self.get_number(x.rel_checkpoint))
        return result

    @staticmethod
    def get_number(rel_checkpoint_str: str = None):
        if rel_checkpoint_str:
            a = re.findall(r"[-+]?\d*\.\d+|\d+", rel_checkpoint_str)
            if a:
                return float(a[-1])
            else:
                return 0
        else:
            return 0

    def group_by_stress(self):
        stress_str_list = []
        grouped_stress = dict()
        for stress_obj in self.stress_obj_list:
            stress_str = stress_obj.rel_stress
            # print(stress_obj.id, grouped_stress.get(stress_str), stress_str, grouped_stress)
            if stress_str in stress_str_list:
                # pre = grouped_stress.get(stress_str)
                grouped_stress.get(stress_str).append(stress_obj)
                # grouped_stress.update({stress_str: pre.append(stress_obj)})
            else:
                stress_str_list.append(stress_str)
                grouped_stress.update({stress_str: [stress_obj]})
                # print(grouped_stress.items())
        return grouped_stress

    def get_total_in_cell(self, stress_pk, config_pk):
        result = filter(lambda row: row.get("FK_RelStress") == stress_pk and row.get("Config_FK") == config_pk,
                        self.completed)
        sn_count = list(result)
        if len(sn_count) == 1:
            return sn_count[0].get("SN_Count")
        else:
            return 0

    def get_failure_count_in_cell(self, stress_pk, config_pk, fm: str = None):
        if isinstance(fm, str):
            result = filter(lambda row: row.get("FK_RelStress") == stress_pk and row.get("Config_FK") == config_pk
                                        and row.get("FailureMode"),
                            self.failures)
        else:
            result = filter(lambda row: row.get("FK_RelStress") == stress_pk and row.get("Config_FK") == config_pk,
                            self.failures)
        sn_count = list(result)
        if len(sn_count) == 1:
            return sn_count[0].get("SN_Count")
        else:
            return 0
        pass

    def get_on_going_in_cell(self, stress_pk, config_pk):
        result = filter(lambda row: row.get("FK_RelStress") == stress_pk and row.get("Config_FK") == config_pk,
                        self.on_going)
        sn_count = list(result)
        if len(sn_count) == 1:
            return sn_count[0].get("SN_Count")
        else:
            return 0
        pass

    def cell_display(self, stress_pk, config_pk):
        total = self.get_total_in_cell(stress_pk, config_pk)
        on_going = self.get_on_going_in_cell(stress_pk, config_pk)
        failure_count = self.get_failure_count_in_cell(stress_pk, config_pk)
        if total == 0 and on_going == 0:
            return ""
        else:
            return f'{failure_count}F/{total} ({on_going})'
