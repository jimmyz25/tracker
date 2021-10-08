import pandas as pd


class RawData:
    def __init__(self):
        self.settings = {
            "encode": "utf-8",
            "start_row": 0,
            "end_row": -1,
            "start_keyword": "starttime",
            "end_keyword": "end",
            "serial_number_indicator": "serial",  # in start_row, which column is for serialNumber
            "start_time_indicator": "start",
            "end_time_indicator": "end",
            "separator": ",",
            "skip_keyword": None,
            "skip_row": None,
            "col_name_set": None
        }
        self.start_time_col_name = None
        self.end_time_col_name = None
        self.sn_col_name = None
        self.col_name_set = None

    def auto_parse(self, file, max_col=10, max_row=20):
        start_kw = self.settings.get("start_keyword")
        end_kw = self.settings.get("end_keyword")
        sn_kw = self.settings.get("serial_number_indicator")
        ambiguous = 0
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
                self.col_name_set = set(lines[start_row].split(sep))
        print("start row", start_row)
        print("separator : ", self.settings.get("separator"))
        print(self.col_name_set)
        result = list(filter(lambda x: start_kw in x.lower(), lines[start_row].split(self.settings.get("separator"))))
        if len(result) == 1:
            self.start_time_col_name = result[0]
        result = list(filter(lambda x: end_kw in x.lower(), lines[start_row].split(self.settings.get("separator"))))
        if len(result) == 1:
            self.end_time_col_name = result[0]
        result = list(filter(lambda x: sn_kw in x.lower(), lines[start_row].split(self.settings.get("separator"))))
        if len(result) == 1:
            self.sn_col_name = result[0]


                    
        
