

from data_model import *
import random
import string
import pandas as pd
import timeit

db = DBsqlite(RMD)
gold = DBsqlite(golden)

db.con.backup(db.db_memory)

print (timeit.timeit(lambda: db.db_memory.execute('SELECT * FROM RelLog_T;'),number=1000))
print (timeit.timeit(lambda: db.cur.execute('SELECT * FROM RelLog_T;'),number=1000))

print (timeit.timeit(lambda: db.db_memory.execute("SELECT Config_SN_T.*, RelLog_T.StartTimestamp, RelLog_T.EndTimestamp,"
                                       "RelLog_T.Notes from Config_SN_T "
                                       "left join RelLog_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and "
                                       " Config_SN_T.SerialNumber = RelLog_T.SerialNumber "
                                       "left join Config_T ON Config_T.PK = Config_SN_T.Config_FK "
                                       "left join RelStress_T ON RelStress_T.PK = Config_SN_T.Stress_FK "),number=1000))

print (timeit.timeit(lambda: db.db_memory.execute("SELECT Config_SN_T.*, RelLog_T.StartTimestamp, RelLog_T.EndTimestamp,"
                                       "RelLog_T.Notes from Config_SN_T "
                                       "left join RelLog_T ON Config_SN_T.DateAdded = RelLog_T.StartTimestamp and "
                                       " Config_SN_T.SerialNumber = RelLog_T.SerialNumber "
                                       "left join Config_T ON Config_T.PK = Config_SN_T.Config_FK "
                                       "left join RelStress_T ON RelStress_T.PK = Config_SN_T.Stress_FK "
                                                  "WHERE RelLog_T.SerialNumber = ?",("41C36MX9YSJM",)),number=10000))

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