import pandas as pd


class RawData:
    def __init__(self):
        self.settings = {
            "encode": "utf-8",
            "start_row": 0,
            "end_row": -1,
            "start_keyword": "starttime",
            "end_keyword": "endtime",
            "serial_number_indicator": "serial",  # in start_row, which column is for serialNumber
            "start_time_indicator": "start",
            "end_time_indicator": "end",
            "separator": ",",
            "skip_keywords": None,
            "skip_row": None,
            "col_name_set": None,
            "sn_col_name_pos": None,
            "start_time_pos": None,
            "end_time_pos": None,
            "start_col": 0
        }
        self.col_name_set = None

    def auto_parse(self, file, max_col=10, max_row=20):
        """
        goal is to locate start column, find all columns with keywords for user to select, and
        create a preview containing all these columns and some data
        when user changed keyword, refresh auto_parse to generate a new preview, until user confirm is ok
        finally, user is able to save the settings.

        :param file:
        :param max_col:
        :param max_row:
        :return:
        """
        start_kw = self.settings.get("start_keyword")
        end_kw = self.settings.get("end_keyword")
        sn_kw = self.settings.get("serial_number_indicator")
        with open(file, 'r', encoding=self.settings.get("encode")) as f:
            data = f.read()
        f.close()
        # data = data.replace(u"\"\n\"", '')
        lines = data.split("\n")
        row_count = min(len(lines), max_row)
        lines = lines[:row_count]
        # determine separator by checking which separator is able to split line with max sections
        pre_max_count = 0
        start_row = 0
        for sep in [",", ";", "\t"]:
            col_count_list = [len(list(filter(lambda x: x != "", line.split(sep))))
                              for line in lines]  # check each row, how many sections
            if max(col_count_list) > pre_max_count:
                pre_max_count = max(col_count_list)
                # from top to max_row, try to see which row has max
                # number of sections, this section is then a candidate for column name
                start_row = col_count_list.index(pre_max_count)
                self.settings.update({"start_row": start_row})
                self.settings.update({"separator": sep})
        col_name_row_separated = lines[start_row].split(self.settings.get("separator"))
        max_col_pos = min(max_col, len(col_name_row_separated))
        print("max_col_pos", max_col_pos)
        self.settings.update({"start_col": self.first_column_index(col_name_row_separated)})
        self.settings.update({"col_name_set": set(col_name_row_separated)})
        result = list(filter(lambda x: start_kw in x.lower(), lines[start_row].split(self.settings.get("separator"))))
        if len(result) == 1:
            self.settings.update({"start_time": result[0]})
        result = list(filter(lambda x: end_kw in x.lower(), lines[start_row].split(self.settings.get("separator"))))
        if len(result) == 1:
            self.settings.update({"end_time": result[0]})
        result = list(filter(lambda x: sn_kw in x.lower(), lines[start_row].split(self.settings.get("separator"))))
        if len(result) == 1:
            self.settings.update({"sn_col_name": result[0]})
        print(self.settings)
        to_display = [self.fill_up_row(max_col_pos, line.split(self.settings.get("separator")))[
                      self.settings.get("start_col"):max_col_pos] for line in lines[start_row:max_row]]
        print(to_display)
        return to_display

    @staticmethod
    def first_column_index(line: list = None):
        for i in range(len(line)):
            if line[i] != "":
                return i
        return None

    def fill_up_row(self, max_col: int, row: list):
        if row:
            if len(row) < max_col:
                delta = max_col - len(row)
                row.append(["" for _ in range(delta)])
            return row
        else:
            return ["" for _ in range(max_col)]

    def row_validation(self, row: list):
        # if skip_keyword in row, remove row
        if self.settings.get("skip_keywords"):
            for keyword in self.settings.get("skip_keywords").split(","):
                if keyword in row:
                    return []
        if isinstance(self.settings.get("start_time_pos"), int):
            row.insert(0,row.pop(self.settings.get("start_time_pos")))


    def clean_up(self, lines: list = None):
        """
        0. confirm start row matches setting. if not, return empty []
        1. remove anything above start_row
        2. remove any row that contains skip keyword
        3. create a df, drop na
        4. bring all character columns to front
        5. rename sn column name, start time column name, end time column name

        :param lines: file
        :return:
        """
        pass
