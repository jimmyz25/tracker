

from data_model import *
import random
import string
import pandas as pd
import timeit

db = DBsqlite(RMD)
gold = DBsqlite(golden)

db.con.backup(db.db_memory)

print (timeit.timeit(lambda: db.db_memory.execute('SELECT * FROM RelLog_T WHERE PK=1;').fetchmany(10),number=1000))
print (timeit.timeit(lambda: db.cur.execute('SELECT * FROM RelLog_T;').fetchmany(10),number=1000))

print (timeit.timeit(lambda: db.db_memory.execute("SELECT Config_SN_T.*, RelLog_T.StartTimestamp, RelLog_T.EndTimestamp,"
                                       "RelLog_T.Notes from Config_SN_T "
                                       "left join RelLog_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and "
                                       " Config_SN_T.SerialNumber = RelLog_T.SerialNumber "
                                       "left join Config_T ON Config_T.PK = Config_SN_T.Config_FK "
                                       "left join RelStress_T ON RelStress_T.PK = Config_SN_T.Stress_FK ORDER BY RelLog_T.StartTimestamp LIMIT 1000").fetchmany(1000),number=100))

print (timeit.timeit(lambda: db.db_memory.execute("SELECT Config_SN_T.*"
                                       " from Config_SN_T "
                                       "inner join RelLog_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and "
                                       " Config_SN_T.SerialNumber = RelLog_T.SerialNumber "
                                       "inner join Config_T ON Config_T.PK = Config_SN_T.Config_FK "
                                       "inner join RelStress_T ON RelStress_T.PK = Config_SN_T.Stress_FK "
                                      "WHERE RelLog_T.SerialNumber like ? and Config_SN_T.WIP =? and Config_SN_T.Config_FK in {} LIMIT 1000 ".format(("asdf","sdfa")),
                                                  ("df%","sadf")).fetchmany(100),number=1000))

print (timeit.timeit(lambda: db.db_memory.execute("SELECT Config_SN_T.*"
                                       " from Config_SN_T,RelLog_T "
                                                  "WHERE Config_SN_T.SerialNumber = RelLog_T.SerialNumber LIMIT 1000").fetchmany(100),number=1000))

print (timeit.timeit(lambda: db.db_memory.execute("SELECT Config_SN_T.*"
                                       " from Config_SN_T Inner Join RelLog_T ON Config_SN_T.SerialNumber = RelLog_T.SerialNumber LIMIT 1000").fetchmany(100),number=1000))
#
# def sort1(self):
#   db.cur.execute('SELECT * FROM RelLog_T;')
#   self._conn.commit()
#
# def sort(self):
#   self.df_employee.sort_values(by='name')
#
#
# def select1(self):
#   self._cursor.execute('SELECT name, dept FROM employee;')
#   self._conn.commit()
#
# def select(self):
#   self.df_employee[["name", "dept"]]
#
# def join1(self):
#     self._cursor.execute('SELECT employee.name, employee.salary + bonus.bonus '
#                          'FROM employee INNER JOIN bonus ON employee.name = bonus.name')
#     self._conn.commit()
#
# def join(self):
#     joined = self.df_employee.merge(self.df_bonus, on='name')
#     joined['total'] = joined['bonus'] + joined['salary']
#
#
# def filter1(self):
#   self._cursor.execute('SELECT * FROM employee WHERE dept = "a";')
#   self._conn.commit()
#
#
# def filter(self):
#   self.df_employee[self.df_employee['dept'] == 'a']

#
# @staticmethod
# def filter_func(x, parameter: str, value_set: set):
#     if isinstance(value_set, set):
#         if len(value_set) == 0:
#             return True
#         else:
#             return x.get(parameter) in value_set
#     else:
#         if isinstance(value_set, str):
#             return x.get(parameter).startswith(value_set)
#         elif isinstance(value_set, int):
#             return x.get(parameter) in {value_set}
#         else:
#             return True