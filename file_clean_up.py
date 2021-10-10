import csv

import pandas as pd
import datetime as dt


class RawData:
    def __init__(self):
        """
       "encode": "utf-8",
            "start_row": 0,
            "end_row": -1,
            "start_keyword": "starttime",
            "end_keyword": "endtime",
            "serial_number_keyword": "serial",  # in start_row, which column is for serialNumber
            "start_time_indicator": "start",
            "end_time_indicator": "end",
            "separator": ",",
            "skip_keywords": None,
            "skip_row": None,
            "col_name_set": None,
            "sn_col": None,
            "start_time_col": None,
            "end_time_col": None,
            "start_col": 0,
            "sn_col_candi": None,
            "start_time_candi": None,
            "end_time_candi": None,
        """
        self.settings = {
            "encode": "utf-8",
            "start_row": 0,
            "end_row": -1,
            "start_keyword": "start",
            "end_keyword": "end",
            "serial_number_keyword": "serial",  # in start_row, which column is for serialNumber
            "start_time_indicator": "start",
            "end_time_indicator": "end",
            "separator": None,
            "skip_keywords": None,
            "skip_rows": None,
            "col_name_set": None,
            "sn_col": None,
            "start_time_col": None,
            "end_time_col": None,
            "start_col": 0,
            "sn_col_candi": None,
            "start_time_candi": None,
            "end_time_candi": None,
            "quotechar": None,
            "timestamp_format": None
        }
        self.col_name_set = None

    def auto_parse(self, file, max_col=10, max_row=20):
        """
        goal is to locate start column, find all columns with keywords for user to select, and
        create a preview containing all these columns and some data
        when user changed keyword, refresh auto_parse to generate a new preview, until user confirm is ok
        finally, user is able to save the settings.



        :param file: which file to preview
        :param max_col: when generating preview, how many columns to display
        :param max_row: when generating preview, how many rows to display
        :return: a preview data set, and in the process, provide list of possible columns for sn, start time and end time
        """
        start_kw = self.settings.get("start_keyword")
        end_kw = self.settings.get("end_keyword")
        sn_kw = self.settings.get("serial_number_keyword")
        with open(file, newline="") as f:
            dialect = csv.Sniffer().sniff(f.readline(max_row))
            f.seek(0)
            csv_reader = csv.reader(f, dialect)
            data = [[cell.strip() for cell in row] for row in csv_reader]
            self.settings.update({"separator": dialect.delimiter})
            self.settings.update({"quotechar": dialect.quotechar})
            row_count = len(data)

            # determine separator by checking which separator is able to split line with max sections
            pre_max_count = 0
            if self.settings.get("start_row"):
                start_row = self.settings.get("start_row")
            else:
                start_row = 0
            if start_row == 0:
                col_count_list = [len(list(filter(lambda x: x != "", line)))
                                  for line in data]  # check each row, how many non-empty sections
                # if max(col_count_list) > pre_max_count:
                pre_max_count = max(col_count_list)
                # from top to max_row, try to see which row has max
                # number of sections, this section is then a candidate for column name
                start_row = col_count_list.index(pre_max_count)
            lines = data[start_row: row_count]
            self.settings.update({"start_row": start_row})
            col_name_row_separated = lines[0]
            max_col_to_display = min(max_col, len(col_name_row_separated))
            sn_col_candidates = list(filter(lambda x: self.settings.get("serial_number_keyword") in x,
                                            col_name_row_separated))
            start_time_candidates = list(
                filter(lambda x: self.settings.get("start_keyword") in x, col_name_row_separated))
            end_time_candidates = list(filter(lambda x: self.settings.get("end_keyword") in x, col_name_row_separated))
            self.settings.update({
                "sn_col_candi": sn_col_candidates,
                "start_time_candi": start_time_candidates,
                "end_time_candi": end_time_candidates,
                "start_col": self.first_column_index(col_name_row_separated),
                "col_name_set": set(col_name_row_separated)
            })
            result = list(filter(lambda x: start_kw.lower() in x.lower(),
                                 lines[0]))
            if len(result) > 0:
                self.settings.update({"start_time_col": result[0]})
            result = list(
                filter(lambda x: end_kw.lower() in x.lower(), lines[0]))
            if len(result) > 0:
                self.settings.update({"end_time_col": result[0]})
            result = list(
                filter(lambda x: sn_kw.lower() in x.lower(), lines[0]))
            if len(result) > 0:
                self.settings.update({"sn_col": result[0]})

            to_display = [self.row_validation(ind, line)[
                          self.settings.get("start_col"):]
                          for ind, line in enumerate(lines[0: row_count])]

            df = pd.DataFrame(to_display[1:], columns=to_display[0])
            if self.settings.get("start_time_col"):
                if self.settings.get("timestamp_format"):
                    try:
                        df[self.settings.get("start_time_col")] = df[self.settings.get("start_time_col")] \
                            .map(lambda x: dt.datetime.strptime(x, self.settings.get("timestamp_format")).timestamp(),
                                 'ignore')
                    except ValueError:
                        print("cannot process timestamp")
                        pass
            header = df.columns.tolist()
            if self.settings.get("sn_col"):
                if self.settings.get("sn_col") in header:
                    sn_index = header.index(self.settings.get("sn_col"))
                    header.insert(0, header.pop(sn_index))
            if self.settings.get("start_time_col"):
                if self.settings.get("start_time_col") in header:
                    start_time_index = header.index(self.settings.get("start_time_col"))
                    header.insert(0, header.pop(start_time_index))
            df = df[header[:max_col_to_display]]
            values = df.values.tolist()
            return [header]+values

    @staticmethod
    def first_column_index(line: list = None):
        for i in range(len(line)):
            if line[i] != "":
                return i
        return None

    @staticmethod
    def fill_up_row(max_col: int, row: list):
        if row:
            if len(row) < max_col:
                delta = max_col - len(row)
                row.append(["" for _ in range(delta)])
            return row
        else:
            return ["" for _ in range(max_col)]

    def row_validation(self, ind: int, row: list):
        # print (row)
        # return row
        # if skip_keyword in row, remove row
        if self.settings.get("skip_keywords"):
            for keyword in self.settings.get("skip_keywords"):
                if keyword in "".join(row):
                    print("row skipped")
                    return []
        if self.settings.get("skip_rows"):
            for row_index in self.settings.get("skip_rows"):
                try:
                    row_index = int(row_index)
                except TypeError:
                    return row
                if ind == row_index:
                    print("row skipped")
                    return []
        return row
        #
        # if isinstance(self.settings.get("start_time_pos"), int):
        #     row.insert(0, row.pop(self.settings.get("start_time_pos")))

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
