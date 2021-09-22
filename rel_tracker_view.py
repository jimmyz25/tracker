import PySimpleGUI as sg


class rel_tracker_view:
    def __init__(self, settings: sg.user_settings):
        self.default_settings = settings

    @staticmethod
    def welcome_page():
        layout1 = [
            [sg.Txt("Rel Logger", size=(None, 1), font=("Helvetica", 50), text_color='White',
                    background_color='#4267B2', justification="right", pad=(5, 40), auto_size_text=True)],
            [sg.Txt("Version 0.1 ", text_color='White', background_color='#4267B2', justification="left",
                    auto_size_text=False)],
            [sg.Txt("from Jimmy Z @facebook. All Right Reserved", text_color='White', background_color='#4267B2',
                    justification="left", auto_size_text=False)]
        ]
        column1 = sg.Column(layout1, background_color="#4267B2", size=(500, 200))
        layout = [[column1]]
        window = sg.Window('Welcome Page', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=True,
                           finalize=True, auto_close=True, auto_close_duration=1, background_color='#4267B2')
        return window

    @staticmethod
    def __facebook__():
        facebook_text = sg.Txt("facebook", border_width=0, text_color="orange", font='Helvetica 30 bold',
                               justification='center', pad=5, key="-Home-", enable_events=True)
        column1 = sg.Column(layout=[[facebook_text]], size=(600, 40))

        return [
            [column1, sg.Stretch(), sg.Txt("FRL project only", font='Heletica 10', text_color='#4267B2', size=(15, 1))]]

    @staticmethod
    def __status__():
        layout_status_column = [
            [sg.Txt("Station", text_color="Black", font='Helvetica 20 bold', key="-station_name-"
                    )],
            [sg.Txt("Last Sync: 24min ago", key="-last_sync-")],
            [sg.Txt("")],
            [sg.Txt("Notes of selected row", key="-additional_info-")],
            [sg.Multiline(size=(40, 8), expand_y=True, no_scrollbar=True, key="-note_show-", disabled=True)]
        ]
        status_column = sg.Column(layout=layout_status_column, size=(200, 180), key="-status-column")
        return status_column

    @staticmethod
    def preference_view():
        layout1 = [
            [sg.Txt("Station Name", size=15),
             sg.InputText(size=30,
                          key="-Station_Name-", tooltip="maximum character: 18"), sg.Stretch(),
             sg.B("Validate", size=10)],
            [sg.Txt("Station Type", size=15),
             sg.Combo(values=["a", "b"], size=30, readonly=True, key="-station-type-", enable_events=True),
             sg.Stretch(),
             sg.B("Set", size=10)],
            [sg.HorizontalSeparator()],
            [sg.Txt("Input Folder", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), tooltip="Input folder where data will be saved before tagging",
                             target=(sg.ThisRow, -2))],
            [sg.Txt("Output Folder", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), target=(sg.ThisRow, -2))],
            [sg.HorizontalSeparator()],
            [sg.Txt("Golden Database", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FileBrowse(size=(10, 1), target=(sg.ThisRow, -2))],
            [sg.Txt("Auto Sync", size=15), sg.Rad("ON", group_id="auto_sync", default=True),
             sg.Rad("OFF", group_id="auto_sync")],
            [sg.Btn("Save Preference", size=15), sg.Btn("New Window", key="-New_Window-")]
        ]

        window = sg.Window('Preference', layout1, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True)
        return window

    def rel_lab_station_view(self):
        tab_new_left = [
            [sg.Txt(text="WIP", size=(15, 1)), sg.In(key="-New-WIP_Input-", enable_events=True)],
            [sg.Txt("Assign Config", size=(15, 1)), sg.In(key="-New-Config_Input-", enable_events=True)],
            [sg.Txt("initial Checkpoint", size=(15, 1)), sg.In(key="-New-Ckp_Input-", enable_events=True)],
            [sg.Txt("Notes", size=(15, 1)), sg.In(key="-New-Note-", enable_events=False)],
            [sg.Txt("SerialNumber (0)", size=(15, 3), expand_y=True, key="-Multi_SN-"),
             sg.Multiline(size=(40, 3), expand_y=True, no_scrollbar=True, enable_events=False, key="-New-SN_Input-",
                          tooltip="multiple SN seperate by comma, enter to count\n Note:duplicates will be removed ")]
        ]
        tab1 = sg.Tab(layout=tab_new_left, title="Register New Unit")

        tab_old_left = [
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-"), sg.In(key="-SN_Input-", enable_events=True)],
            [sg.Txt(text="WIP", size=(15, 1), key="-display_wip-"), sg.In(key="-WIP_Input-", enable_events=True)],
            [sg.Txt("Config", size=(15, 1), key="-display-config"), sg.In("", disabled=True, key="-Config_Input-")],
            [sg.Txt("Current Checkpoint", size=(15, 1), key="-display-ckp"),
             sg.In("", disabled=True, key="-Ckp_Input-")],
            [sg.Txt("Notes", size=(15, 3), expand_y=True),
             sg.Multiline(size=(40, 3), expand_y=True, no_scrollbar=True, key="-Note-")]
        ]

        tab2 = sg.Tab(layout=tab_old_left, title="Existing Units")

        tab_group = sg.TabGroup(layout=[[tab1, tab2]], size=(400, 180), enable_events=True, key="-Tab_Selection-")

        layout_button_column = [
            [sg.B("Add", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],
            [sg.B("Reset", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=False)],
            [sg.B("Update", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],
            [sg.B("CheckIn", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],
            [sg.B("Checkout", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],
            [sg.B("Delete", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],

        ]
        button_column = sg.Column(layout=layout_button_column, size=(200, 200))

        table_col = ['PK', 'Config', 'WIP', 'SerialNumber', 'Stress', 'Checkpoint', 'Start', 'End',
                     'Note']
        show_heading = [False, True, True, True, True, True, True, True, True]
        table_value = [[str(row) for row in range(9)] for col in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col,
                              expand_x=True, num_rows=15, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white", right_click_menu=['&right_click', ["update", "remove"]],
                              enable_events=True, key="-table_select-", pad=(5, 10), hide_vertical_scroll=True)
        # output_view = sg.Output(size=(120, 5), background_color="white",expand_x=True, key="-output-")

        layout = [
            [self.__facebook__()],
            [tab_group, button_column, self.__status__(), sg.Stretch()],
            [sg.Txt("Latest Checkpoint Only", size=20),
             sg.Rad("T", group_id="table_show_latest", default=False, enable_events=True, key="-show_latest1-"),
             sg.Rad("F", group_id="table_show_latest", default=True, enable_events=True, key="-show_latest0-")],
            [table_view],
            # [output_view]
        ]

        window = sg.Window('Rel Status Logger', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True)
        window["-Config_Input-"].bind("<Button-1>", "-ConfigPop-")
        window["-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")
        window["-New-Config_Input-"].bind("<Button-1>", "-ConfigPop-")
        window["-New-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")
        window["-New-SN_Input-"].bind("<Return>", "-sn_count-")
        window["-New-SN_Input-"].bind("<,>", "2-sn_count-")

        return window

    @staticmethod
    def popup_config_select():
        layout1 = [
            [sg.Txt("Program", size=15),
             sg.InputCombo(size=30, values=[], key="Program", enable_events=True), sg.Stretch(),
             sg.B("Clear", size=10)],
            [sg.Txt("Build", size=15), sg.InputCombo(values=[], size=30, readonly=True,
                                                     key="Build", enable_events=True), sg.Stretch()],
            [sg.Txt("Config", size=15), sg.InputCombo(values=[], size=30, readonly=True,
                                                      key="Config", enable_events=True), sg.Stretch()],
            [sg.B("Save and Close", enable_events=True, key="-Save-"), sg.B("Clear", enable_events=True, key="-Clear-")]

        ]

        window = sg.Window('Config Selection', layout1, keep_on_top=True, grab_anywhere=True, no_titlebar=False,
                           finalize=True, modal=True)
        window["Program"].bind("<KeyPress>", "-KeyPress")
        window.TKroot.grab_set()

        return window

    @staticmethod
    def popup_stress_select():
        layout1 = [
            [sg.Txt("RelStress", size=15),
             sg.InputCombo(size=30, values=[], key="RelStress", enable_events=True), sg.Stretch()],
            [sg.Txt("RelCheckpoint", size=15), sg.InputCombo(values=[], size=30, readonly=True,
                                                             key="RelCheckpoint", enable_events=True), sg.Stretch()],
            [sg.B("Save and Close", enable_events=True, key="-Save-"), sg.B("Clear", enable_events=True, key="-Clear-")]

        ]

        window = sg.Window('Stress Selection', layout1, keep_on_top=True, grab_anywhere=True, no_titlebar=False,
                           finalize=True, modal=True)
        window["RelStress"].bind("<KeyPress>", "-KeyPress")
        window.TKroot.grab_set()
        return window

    @staticmethod
    def popup_fm_select():
        layout_filter_column = [

            [sg.Txt("Failure Mode Sets", size=(15, 1)),
             sg.Combo(["cosmetic inspection set 1", "cosmetic inspection set 2"], disabled=False,
                      key="-failure_mode_set-", size=(20, 1),enable_events=True)],
            [sg.Txt("Failure Mode", size=(15, 1)),
             sg.Listbox(values=["failure mode 1", "failure mode 2"], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        size=(20, 11),key="-failure_to_select-",enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column)

        layout_button_column = [
            [sg.Sizer(10,50)],
            [sg.B("Add >>>", size=(10, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True,key="-Add-")],
            [sg.B("Remove <<<", size=(10, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True,key="-Remove-")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)
        table_col = ['PK','failure mode set', 'failure mode', 'detail']
        show_heading = [False, True, True, True]
        table_value = [[str(row) for row in range(4)] for col in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col,size=(40,10),
                              expand_x=True, num_rows=12, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white", right_click_menu=['&right_click', ["update", "remove"]],
                              enable_events=True, key="-highlighted_failures-", pad=(5, 10), hide_vertical_scroll=True)

        layout_done_column = [
             [table_view],
            [sg.VStretch()]

        ]

        done_column = sg.Column(layout=layout_done_column)

        layout = [
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-"),
             sg.In(key="-SN_Input-", disabled=True, size=(20, 1))],
            [sg.Txt("Current Checkpoint", size=(15, 1)),
             sg.In("", disabled=True, key="-Ckp_Input-", size=(20, 1))],
            [filter_column, button_column, done_column],
            [sg.B("Add details", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],
            [sg.Multiline(default_text="", size=(40, 15),expand_x=True)]
        ]

        window = sg.Window('Update Failure Mode', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False)
        window["-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")
        return window

    @staticmethod
    def popup_fm_config():
        layout_filter_column = [
            [sg.Txt("Failure Mode Sets", size=(15, 1)),
             sg.Combo(["cosmetic inspection set 1", "cosmetic inspection set 2"], disabled=False,
                      key="-failure_mode_set-", size=(20, 1))],
            [sg.Txt("Failure Mode", size=(15, 1)),
             sg.Listbox(values=["failure mode 1", "failure mode 2"], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        size=(20, 10))],
        ]

        filter_column = sg.Column(layout=layout_filter_column)

        layout_button_column = [
            [sg.B("Group Failure Modes", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=False,
                  tooltip="each failure mode can only belongs to one group")],
            [sg.B("Create New Failure Mode", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=False)],
            [sg.B("Delete Failure Mode", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=False)],
        ]
        button_column = sg.Column(layout=layout_button_column,expand_y=True)

        layout = [
            [filter_column, button_column],
        ]

        window = sg.Window('Config Failure Mode', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False)
        return window

    def fa_log_view(self):
        table_col = ['PK', 'SerialNumber', 'Stress', 'Checkpoint']
        show_heading = [False, True, True, True]
        table_value = [[str(row) for row in range(4)] for col in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col, select_mode=sg.SELECT_MODE_BROWSE,
                              expand_x=True, num_rows=4, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white", right_click_menu=['&right_click', ["update", "remove"]],
                              enable_events=True, key="-table_select-", pad=(5, 5), hide_vertical_scroll=True)

        layout_filter_column = [
            [sg.Txt("---Filters", size=(40, 1))],
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-"), sg.In(key="-SN_Input-", enable_events=True)],
            [sg.Txt(text="WIP", size=(15, 1), key="-display_wip-"), sg.In(key="-WIP_Input-", enable_events=True)],
            [sg.Txt("Config", size=(15, 1), key="-display-config"), sg.In("", disabled=True, key="-Config_Input-")],
            [sg.Txt("Current Checkpoint", size=(15, 1), key="-display-ckp"),
             sg.In("", disabled=True, key="-Ckp_Input-")],
            [sg.Txt("Failure Mode", size=(15, 1)),
             sg.In("", disabled=False, key="-Failure_Mode_Input-")],
        ]

        filter_column = sg.Column(layout=layout_filter_column,size=(300, 150),)

        layout_button_column = [
            [sg.Txt("Station", text_color="Black", font='Helvetica 20 bold', key="-station_name-"
                    )],
            [sg.B("Reset Filter", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=False)],
            [sg.B("Configure Failure Modes", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=False)],
            [sg.B("Report Failure", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],
            [sg.B("Update Failure", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled_button_color=("#e9f4fa", "#a8d8eb"), disabled=True)],
        ]
        button_column = sg.Column(layout=layout_button_column, size=(200, 150), expand_y=True)

        layout_status_column = [
            [sg.Txt("---SerialNumber to select", size=(40, 1))],
            [sg.Txt("Last Checkpoint Only", size=20),
             sg.Rad("T", group_id="table_show_latest", default=False, enable_events=True, key="-show_latest1-"),
             sg.Rad("F", group_id="table_show_latest", default=True, enable_events=True, key="-show_latest0-")],
            [table_view],
        ]
        status_column = sg.Column(layout=layout_status_column, size=(300, 150), key="-status-column")

        table_col = ['PK', 'Failure Group', 'Failure Mode', 'SerialNumber', 'Stress', 'Checkpoint', 'DateAdded',"Detail"]
        show_heading = [False, True, True, True, True, True, True, True]
        table_value2 = [[str(row) for row in range(8)] for col in range(1)]
        table_view2 = sg.Table(values=table_value2, visible_column_map=show_heading,
                               headings=table_col,
                               expand_x=True, num_rows=15, font="Helvetica 12", header_font="Helvetica 12 bold",
                               header_background_color="white",
                               enable_events=True, key="-fa_table_select-", pad=(5, 10), hide_vertical_scroll=True)

        # output_view = sg.Output(size=(120, 5), background_color="white",expand_x=True, key="-output-")

        layout = [
            [self.__facebook__()],
            [filter_column, status_column, button_column, sg.Stretch()],
            [table_view2]
            # [output_view]
        ]

        window = sg.Window('failure mode logger', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True)
        window["-Config_Input-"].bind("<Button-1>", "-ConfigPop-")
        window["-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")

        return window
