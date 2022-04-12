# import OS module
import os
import sqlite3
import datetime as dt

# Get the list of all files and directories
path = "/Users/jimmyzhong/Desktop/test lib/"
sub_folder = os.path.join(path, ".bf")
db_address = os.path.join(sub_folder, "BillFish.db")
dir_list = os.listdir(sub_folder)

print("Files and directories in '", path, "' :")

# prints all files
print(dir_list)


class ImageDB:
    def __init__(self, address):
        self.__address__ = address
        self.__connect__()
        pass

    def __connect__(self):
        self.con = sqlite3.connect(self.__address__)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def __disconnect__(self):
        self.con.close()

    def add_tag(self, group: str = None, tag: str = None):

        pass

    def get_tag_id(self,tag:str = None):
        if isinstance(tag,str):
            sql = "SELECT id from bf_tag where name = ? LIMIT one"
            result = self.cur.execute(sql, (tag,)).fetchone()
            if result:
                return id
            else:
                return None
        else:
            return None

    def insert_tag(self,tag:str = None):
        if isinstance(tag,str):
            current_time = dt.datetime.now().timestamp()
            sql = "INSERT INTO bf_tag (name,color,born) VALUES (?,?,?) "
            self.cur.execute(sql,(tag,0,current_time))
            self.con.commit()

    def get_group_id(self, group:str = None):
        if isinstance(group,str):
            sql = "SELECT id from bf_tag_group where name = ? LIMIT one"
            result = self.cur.execute(sql, (group,)).fetchone()
            if result:
                return result
            else:
                return None
        else:
            return None


