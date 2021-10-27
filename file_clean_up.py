import csv
import pandas as pd
# import datetime as dt
from data_model import *


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
        :return: a preview data set, and in the process, provide list of possible columns for sn,
         start time and end time
        """
        start_kw = self.settings.get("start_keyword")
        end_kw = self.settings.get("end_keyword")
        sn_kw = self.settings.get("serial_number_keyword")
        with open(file, newline="") as f:
            try:
                dialect = csv.Sniffer().sniff(f.readline(max_row))
            except csv.Error:
                dialect = csv.unix_dialect
            f.seek(0)
            try:
                csv_reader = csv.reader(f, dialect)
            except csv.Error:
                print("not able to read this file")
                return [["" for _ in range(10)] for _ in range(1)]
            data = [[cell.strip() for cell in row] for row in csv_reader]
            self.settings.update({"separator": dialect.delimiter})
            self.settings.update({"quotechar": dialect.quotechar})
            row_count = len(data)
            if self.settings.get("start_row"):
                start_row = self.settings.get("start_row")
            else:
                start_row = 0
            if start_row == 0:
                col_count_list = [len(list(filter(lambda x: x != "", line)))
                                  for line in data[:min(10, row_count)]]  # check each row, how many non-empty sections
                pre_max_count = max(col_count_list)  # find maximum in the first 10 rows
                # from top to max_row, try to see which row has max
                # number of sections, this section is then a candidate for column name
                start_row = col_count_list.index(pre_max_count)
                self.settings.update({"start_row": start_row})
            # for ind, line in enumerate(lines):
            #     print(ind)
            col_name_row_separated = data[start_row]
            print(col_name_row_separated)
            max_col_to_display = min(max_col, len(col_name_row_separated))
            col_length = len(col_name_row_separated)
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
                                 data[start_row]))
            if len(result) > 0:
                self.settings.update({"start_time_col": result[0]})
            result = list(
                filter(lambda x: end_kw.lower() in x.lower(), data[start_row]))
            if len(result) > 0:
                self.settings.update({"end_time_col": result[0]})
            result = list(
                filter(lambda x: sn_kw.lower() in x.lower(), data[start_row]))
            if len(result) > 0:
                self.settings.update({"sn_col": result[0]})
            all_data = [self.row_validation(ind, this_row=line, row_count=row_count, row_length=col_length)[
                        self.settings.get("start_col"):]
                        for ind, line in enumerate(data)]
            # all_data = [self.row_validation(ind=ind, row=line, row_count=row_count, row_length=col_length)
            #             for ind, line in enumerate(data)]
            df = pd.DataFrame(all_data[start_row + 1:], columns=all_data[start_row])
            if self.settings.get("start_time_col"):
                if self.settings.get("timestamp_format"):
                    df[self.settings.get("start_time_col")] = df[self.settings.get("start_time_col")] \
                        .map(lambda x: self.get_timestamp(x),
                             'ignore')
                    # try:
                    #     df[self.settings.get("start_time_col")] = df[self.settings.get("start_time_col")] \
                    #         .map(lambda x: self.get_timestamp(x),
                    #              'ignore')
                    # except ValueError:
                    #     print("cannot process timestamp")
                    #     pass
                    # except KeyError:
                    #     print("cannot find column names")
            header = df.columns.tolist()
            if self.settings.get("sn_col"):
                if self.settings.get("sn_col") in header:
                    sn_index = header.index(self.settings.get("sn_col"))
                    header.insert(0, header.pop(sn_index))
            if self.settings.get("start_time_col"):
                if self.settings.get("start_time_col") in header:
                    start_time_index = header.index(self.settings.get("start_time_col"))
                    header.insert(0, header.pop(start_time_index))
            # df = df[header]
            header = header[:max_col_to_display]
            df = df[header]
            values = df.head(10).values.tolist()

            header_top = ["head"] + header
            values = [[i + start_row + 1] + row for i, row in enumerate(values)]
            header_tail = ["tail"] + header
            if max_row > 5:
                values_tail = df.tail(5).values.tolist()
                values_tail = [[i - 5] + row for i, row in enumerate(values_tail)]
                return [header_top] + values + [header_tail] + values_tail
            else:
                return [header_top] + values

    @staticmethod
    def first_column_index(line: list = None):
        for i in range(len(line)):
            if line[i] != "":
                return i
        return None

    @classmethod
    def fill_up_row(cls, max_col: int, row_to_fil: list):
        if isinstance(row_to_fil, list):
            length_of_row = len(row_to_fil)
            if length_of_row < max_col:
                delta = max_col - len(row_to_fil)
                row_to_fil.extend(["" for _ in range(delta)])
                return row_to_fil
            elif length_of_row > max_col:
                return row_to_fil[:max_col]
            else:
                return row_to_fil
        else:
            return ["" for _ in range(max_col)]

    def row_validation(self, ind: int, this_row: list, row_count: int, row_length: int):
        # print (row)
        # return row
        # if skip_keyword in row, remove row
        current_row = this_row
        if current_row is None:
            return RawData.fill_up_row(max_col=row_length, row_to_fil=[])
        else:
            current_row = this_row
            if self.settings.get("skip_keywords"):
                for keyword in self.settings.get("skip_keywords"):
                    if keyword in "".join(this_row):
                        print("row skipped")
                        return RawData.fill_up_row(max_col=row_length, row_to_fil=[])
            elif self.settings.get("skip_rows"):
                for row_index in self.settings.get("skip_rows"):
                    if row_index.strip('-').isnumeric():
                        row_index = int(row_index)
                        if ind == row_index or row_count + row_index == ind:
                            return RawData.fill_up_row(max_col=row_length, row_to_fil=[])
                return RawData.fill_up_row(max_col=row_length, row_to_fil=current_row)
            return RawData.fill_up_row(max_col=row_length, row_to_fil=current_row)
        #
        # if isinstance(self.settings.get("start_time_pos"), int):
        #     row.insert(0, row.pop(self.settings.get("start_time_pos")))

    def search_match_in_files(self, file_path_list: list):
        ok_to_process_file_list = []
        for file in file_path_list:
            if file.lower().endswith(".csv"):
                with open(file, newline='') as csvfile:
                    try:
                        reader = csv.reader(csvfile, delimiter=self.settings.get("separator"),
                                            quotechar=self.settings.get("quotechar"))
                        limited_row = []
                        for index, row in enumerate(reader):
                            if index > 10:
                                break
                            limited_row.append(row)
                        data = [[cell.strip() for cell in row] for row in limited_row]
                        if len(data) > 1:
                            column_name = set(data[self.settings.get("start_row")])
                            if len(column_name) > 0:
                                if len(column_name - self.settings.get("col_name_set")) / len(column_name) < 0.1 and \
                                        self.settings.get("sn_col") in column_name and \
                                        self.settings.get("start_time_col") in column_name:
                                    ok_to_process_file_list.append(file)
                    except csv.Error as e:
                        print(e)
        return [[row] for row in ok_to_process_file_list]

    def clean_up_file(self, file: str):
        """
        0. confirm start row matches setting. if not, return empty [], completed in other function
        1. remove anything above start_row
        2. remove any row that contains skip keyword
        3. create a list of df each time line sees a header row
        :param file: pre validated file that's ok to proceed
        :return: a list of df
        """
        frame = []
        with open(file, newline='') as csvfile:
            try:
                reader = csv.reader(csvfile, delimiter=self.settings.get("separator"),
                                    quotechar=self.settings.get("quotechar"))
                lines = [[cell.strip() for cell in row] for row in reader]
                row_count = len(lines)
                header_initial = lines[self.settings.get("start_row")][0]
                header_column_count = len(lines[self.settings.get("start_row")])
                header = []
                values = []
                for ind, line in enumerate(lines):
                    if line[0] == header_initial:
                        if len(header) > 0:
                            df = pd.DataFrame(columns=header, data=values)
                            column_names = [i for i in list(df) if i != ""]
                            df = df[column_names]
                            frame.append(df)
                            values = []
                        header = line  # get new header
                        header_column_count = len(header)
                    else:
                        new_row = self.row_validation(ind=ind,
                                                      this_row=line,
                                                      row_count=row_count, row_length=header_column_count)
                        if len(list(filter(lambda x: x != "", new_row))) > 0:
                            values.append(new_row)
                df = pd.DataFrame(columns=header, data=values)
                column_names = [i for i in list(df) if i != ""]
                df = df[column_names]
                frame.append(df)

            except csv.Error as e:
                print(e)
        return frame

    @staticmethod
    def rel_tagging(s, db: DBsqlite, sn_col_name):
        """
        WIP, StartTimestamp, RelStress_T.RelStress, RelStress_T.RelCheckpoint,Config_T.Program," \
                      " Config_T.Build,Config_T.Config
        """
        result = db.rel_tagging(s[sn_col_name], s["StartTimestamp"])
        s["WIP"] = result[0]
        s["StartTimestamp"] = result[1]
        s["RelStress"] = result[2]
        s["RelCheckpoint"] = result[3]
        s["Program"] = result[4]
        s["Build"] = result[5]
        s["Config"] = result[6]
        return s

    def concat_matching_files(self, file_list: list, db: DBsqlite):
        if isinstance(file_list, list):
            sn_col_name = self.settings.get('sn_col')
            frame = []
            for file in file_list:
                print(file)
                subframe = self.clean_up_file(file[0])
                if subframe:
                    frame.extend(subframe)
            df = pd.concat(frame, sort=False, ignore_index=True)
            if self.settings.get('start_time_col') in df.columns.values.tolist():
                df['StartTimestamp'] = df[self.settings.get('start_time_col')] \
                    .map(lambda x: self.get_timestamp(x), na_action='ignore')
                df = df.apply(lambda x: self.rel_tagging(x, db, sn_col_name), axis=1)
                # df = df.dropna(how="all")
            return df
        else:
            return None

    def get_timestamp(self, time_string: str):
        if isinstance(time_string, str):
            try:
                time_string = time_string.strip()
                if time_string != "":
                    timestamp = dt.datetime.strptime(time_string, self.settings.get("timestamp_format")).timestamp()
                    return timestamp
            except ValueError:
                return None
