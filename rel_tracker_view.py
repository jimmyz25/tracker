import PySimpleGUI as sg


# import tkinter.font as tkf
# import tkinter as tk


# def get_scale():
#     # root = tk.Tk()
#     # widget = tk.Label(root, text="My String")
#     # widget.pack()
#     # height = (tkf.Font(font=widget['font']).metrics('linespace'))
#     # scale = int(height / 16)
#     return 1


class rel_tracker_view:
    scale = 1

    def __init__(self, settings: sg.user_settings):
        self.default_settings = settings

    @staticmethod
    def welcome_page():
        layout1 = [
            [sg.Txt("Rel Logger", size=(None, 1), font=("Helvetica", 50), text_color='White',
                    background_color='#4267B2', justification="right", pad=(5, 40), auto_size_text=True)],
            [sg.Txt("Version 0.1 ", text_color='White', background_color='#4267B2', justification="left",
                    auto_size_text=False, key="-version-")],
            [sg.Txt("from Jimmy Z @facebook. All Right Reserved", text_color='White', background_color='#4267B2',
                    justification="left", auto_size_text=False)]
        ]
        column1 = sg.Column(layout1, background_color="#4267B2",
                            size=(int(600 * rel_tracker_view.scale), int(300 * rel_tracker_view.scale)))
        layout = [[column1]]
        window = sg.Window('Welcome Page', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=True,
                           finalize=True, auto_close=True, auto_close_duration=1, background_color='#4267B2')
        print(window["-version-"].get_size())
        rel_tracker_view.scale = window["-version-"].get_size()[0] / 249
        return window

    @staticmethod
    def __facebook__():
        facebook_text = sg.Txt("facebook", border_width=0, text_color="orange", font='Helvetica 30 bold',
                               justification='center', pad=5, key="-Home-", enable_events=True)
        column1 = sg.Column(layout=[[facebook_text]],
                            size=(int(600 * rel_tracker_view.scale), int(40 * rel_tracker_view.scale)))

        return [
            [column1, sg.Stretch(),
             sg.Txt("FRL project only", font='Helvetica 10', text_color='#4267B2', size=(15, 1))]]

    @staticmethod
    def __station_name__():
        text = sg.Txt("Station", text_color="Black", font='Helvetica 15 bold', key="-station_name-"
                      )
        return text

    @staticmethod
    def preference_view():
        layout1 = [
            [sg.Txt("Station Name", size=15),
             sg.InputText(size=30,
                          key="-Station_Name-", tooltip="maximum character: 18"), sg.Stretch(),
             ],
            [sg.Txt("Station Type", size=15),
             sg.Combo(values=[], size=30, readonly=True, key="-station-type-", enable_events=True),
             sg.B("Go"),
             sg.Stretch(),
             ],
            [sg.HorizontalSeparator()],
            [sg.Txt("Input Folder", size=15), sg.InputText(size=30, readonly=True, key="-Input_Folder-"), sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), tooltip="Input folder where data will be saved before tagging",
                             target=(sg.ThisRow, -2), key="input_folder_browse", disabled=True)],
            [sg.Txt("Output Folder", size=15), sg.InputText(size=30, readonly=True,
                                                            key="-Output_Folder-"),
             sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), target=(sg.ThisRow, -2), key="output_folder_browse", disabled=True,)],
            [sg.HorizontalSeparator()],
            [sg.Txt("Golden Database", size=15), sg.InputText(size=30,
                                                              readonly=True,
                                                              key="-Golden_Database-", enable_events=True),
             sg.Stretch(),
             sg.FileBrowse(size=(10, 1), target=(sg.ThisRow, -2), key="-add_golden_address-", enable_events=True)],
            [sg.Txt("Local Database", size=15), sg.InputText(size=30, readonly=True, key="-Local_Database-",
                                                             enable_events=True),
             sg.Stretch(),
             sg.FileBrowse(size=(10, 1), target=(sg.ThisRow, -2))],
            [sg.Txt("Auto Sync", size=15), sg.Rad("ON", group_id="auto_sync", default=True),
             sg.Rad("OFF", group_id="auto_sync")],
            [sg.Btn("Configs Setup", size=15), sg.Btn("Stress Setup", size=15)],
            [sg.Btn("Save Preference", size=15), sg.Btn("Sync with Golden", size=15)]
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
                          tooltip="copy paste from csv or manually enter, finish with RETURN \n Note:duplicates will "
                                  "be removed ")]
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

        tab_group = sg.TabGroup(layout=[[tab1, tab2]],
                                size=(int(350 * rel_tracker_view.scale), int(180 * rel_tracker_view.scale)),
                                enable_events=True, key="-Tab_Selection-")

        layout_button_column = [
            [sg.B("Add", size=(20, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="register new units in batch"),
             sg.B("Assign WIP", size=(20, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="select or enter existing units then fill in WIP in 'register new unit' tab ")
             ],
            [sg.B("Reset", size=(20, 1), pad=(5, 2),
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="reset filter"),
             sg.B("Update", size=(20, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="only available in update mode")],
            [sg.B("CheckIn", size=(20, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="check in selected units to new checkpoints \n"
                          "Note: only available to latest status row"),
             sg.B("Checkout", size=(20, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="checkout current checkpoint to indicate completion of checkpoint")
             ],
            [sg.B("Delete", size=(20, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab"),
             sg.B("Add Dummy SN", size=(20, 1), pad=(5, 2),
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="only for demo, disabled for normal use")
             ],
            [sg.B("Remove for FA", size=(20, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="assign selected row to WIP: 'FA' "),
             sg.B("Show Summary", size=(20, 1), pad=(5, 2),
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="generate a summary to show test status")
             ]
        ]
        button_column = sg.Column(layout=layout_button_column,
                                  size=(int(320 * rel_tracker_view.scale), int(180 * rel_tracker_view.scale)))

        table_col = ['PK', 'Config', 'WIP', 'SerialNumber', 'Stress', 'Checkpoint', 'Start', 'End',
                     'Note']
        show_heading = [False, True, True, True, True, True, True, True, True]
        table_value = [[str(row) for row in range(9)] for _ in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col,
                              expand_x=True, num_rows=15, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white",
                              right_click_menu=['&right_click', ["Enter Update Mode", "Exit Update Mode"]],
                              enable_events=True, key="-table_select-", pad=(5, 10), hide_vertical_scroll=True)
        # output_view = sg.Output(size=(130, 5), background_color="white",expand_x=True, key="-output-")
        layout_status_column = [
            [self.__station_name__()],
            [sg.Txt("Last Sync: 24min ago", key="-last_sync-")],
            [sg.Txt("Latest Checkpoint Only", size=20),
             sg.Rad("T", group_id="table_show_latest", default=False, enable_events=True, key="-show_latest1-"),
             sg.Rad("F", group_id="table_show_latest", default=True, enable_events=True, key="-show_latest0-")],
            [sg.Txt("Current Station Only", size=20),
             sg.Rad("T", group_id="table_show_current_station",
                    default=False, enable_events=True, key="-show_current1-"),
             sg.Rad("F", group_id="table_show_current_station",
                    default=True, enable_events=True, key="-show_current0-")],
            [sg.Txt("")]
        ]
        status_column = sg.Column(layout=layout_status_column,
                                  size=(int(250 * rel_tracker_view.scale), int(150 * rel_tracker_view.scale)),
                                  key="-status-column")
        layout = [
            [self.__facebook__()],
            [tab_group, button_column, status_column, sg.Stretch()],
            [table_view],
            # [output_view]
        ]

        window = sg.Window('Rel Status Logger', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True, default_button_element_size=(5, 1))
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
             ],
            [sg.Txt("Build", size=15), sg.InputCombo(values=[], size=30, readonly=True,
                                                     key="Build", enable_events=True), sg.Stretch()],
            [sg.Txt("Config", size=15), sg.InputCombo(values=[], size=30, readonly=True,
                                                      key="Config", enable_events=True), sg.Stretch()],
            [sg.B("Save and Close", enable_events=True, key="-Save-", size=(25, 1)),
             sg.B("Clear", enable_events=True, key="-Clear-")]

        ]

        window = sg.Window('Config Selection', layout1, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, modal=True)
        window["Program"].bind("<KeyPress>", "-KeyPress")
        # window.TKroot.grab_set()

        return window

    @staticmethod
    def popup_stress_select():
        layout1 = [
            [sg.Txt("RelStress", size=15),
             sg.InputCombo(size=30, values=[], key="RelStress", enable_events=True), sg.Stretch()],
            [sg.Txt("RelCheckpoint", size=15), sg.InputCombo(values=[], size=30, readonly=True,
                                                             key="RelCheckpoint", enable_events=True), sg.Stretch()],
            [sg.B("Save and Close", enable_events=True, key="-Save-", size=(25, 1)),
             sg.B("Clear", enable_events=True, key="-Clear-")]

        ]

        window = sg.Window('Stress Selection', layout1, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, modal=True)
        window["RelStress"].bind("<KeyPress>", "-KeyPress")
        # window.TKroot.grab_set()
        return window

    @staticmethod
    def popup_fm_select():
        layout_filter_column = [

            [sg.Txt("Failure Mode Sets", size=(15, 1)),
             sg.Combo(["cosmetic inspection set 1", "cosmetic inspection set 2"], disabled=False,
                      key="-failure_mode_set-", size=(20, 1), enable_events=True)],
            [sg.Txt("Failure Mode", size=(15, 1)),
             sg.Listbox(values=["failure mode 1", "failure mode 2"], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        size=(20, 11), key="-failure_to_select-", enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column)

        layout_button_column = [
            [sg.Sizer(10, 50)],
            [sg.B("Add >>>", size=(10, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, key="-Add-", disabled_button_color="#ababab")],
            [sg.B("Remove <<<", size=(10, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, key="-Remove-", disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)
        table_col = ['PK', 'failure mode set', 'failure mode', 'detail']
        show_heading = [False, True, True, True]
        table_value = [[str(row) for row in range(4)] for _ in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col, size=(40, 10),
                              expand_x=True, num_rows=12, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white",
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
                  disabled=True, disabled_button_color="#ababab")],
            [sg.Multiline(default_text="", size=(40, 15), expand_x=True, key="-fa-detail-")]
        ]

        window = sg.Window('Update Failure Mode', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        window["-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")
        return window

    @staticmethod
    def popup_fm_config():
        layout_filter_column = [
            [sg.Txt("Failure Mode Group", size=(15, 1)),
             sg.Combo(["cosmetic inspection set 1", "cosmetic inspection set 2"], disabled=False, enable_events=True,
                      key="-failure_mode_set-", size=(20, 1))],
            [sg.Txt("Failure Mode", size=(15, 1)),
             sg.Listbox(values=["failure mode 1", "failure mode 2"], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        size=(20, 10), key="-failure_mode_list-", enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column)

        layout_button_column = [
            [sg.B("Group Failure Modes", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="each failure mode can only belongs to one group")],
            [sg.B("Create New Failure Mode", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=False, disabled_button_color="#ababab")],
            [sg.B("Archive Failure Mode", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)

        layout = [
            [filter_column, button_column],
        ]

        window = sg.Window('Config Failure Mode', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        return window

    def fa_log_view(self):
        table_col = ['PK', '   SerialNumber   ', '   Stress   ', '   Checkpoint   ', "   Config   ", "   EndTime   "]
        show_heading = [False, True, True, True, True, True]
        table_value = [[str(row) for row in range(6)] for _ in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col, select_mode=sg.SELECT_MODE_BROWSE,
                              expand_x=True, num_rows=11, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white",
                              enable_events=True, key="-table_select-", pad=(5, 5), hide_vertical_scroll=True)

        layout_filter_column = [
            [self.__station_name__()],
            [sg.Txt("Last Checkpoint Only", size=20),
             sg.Rad("T", group_id="table_show_latest", default=False, enable_events=True, key="-show_latest1-"),
             sg.Rad("F", group_id="table_show_latest", default=True, enable_events=True, key="-show_latest0-")],
            [sg.Txt("Current Station Only", size=20),
             sg.Rad("T", group_id="table_show_current_station", default=False, enable_events=True,
                    key="-show_current1-"),
             sg.Rad("F", group_id="table_show_current_station", default=True, enable_events=True,
                    key="-show_current0-")],
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-"), sg.In(key="-SN_Input-", enable_events=True)],
            [sg.Txt(text="WIP", size=(15, 1), key="-display_wip-"), sg.In(key="-WIP_Input-", enable_events=True)],
            [sg.Txt("Config", size=(15, 1), key="-display-config"), sg.In("", disabled=True, key="-Config_Input-")],
            [sg.Txt("Current Checkpoint", size=(15, 1), key="-display-ckp"),
             sg.In("", disabled=True, key="-Ckp_Input-")],
            [sg.Txt("Failure Mode", size=(15, 1)),
             sg.In("", disabled=False, key="-Failure_Mode_Input-", enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column,
                                  size=(int(330 * rel_tracker_view.scale), int(220 * rel_tracker_view.scale)), )

        layout_button_row = [
            sg.B("Reset Filter", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                 disabled=False, disabled_button_color="#ababab"),
            sg.B("Edit Failure Modes", size=(25, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                 disabled=False, disabled_button_color="#ababab"),
            sg.B("Report Failure", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                 disabled=True, disabled_button_color="#ababab"),
            sg.B("Show Summary", size=(20, 1), pad=(5, 2),
                 disabled=False, disabled_button_color="#ababab")
        ]

        table_col = ['PK', 'Failure Group', 'Failure Mode', 'SerialNumber', 'Stress', 'Checkpoint', 'DateAdded',
                     "Detail"]
        show_heading = [False, True, True, True, True, True, True, True]
        table_value2 = [[str(row) for row in range(8)] for _ in range(1)]
        table_view2 = sg.Table(values=table_value2, visible_column_map=show_heading,
                               headings=table_col, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                               expand_x=True, num_rows=15, font="Helvetica 12", header_font="Helvetica 12 bold",
                               header_background_color="white",
                               enable_events=False, key="-fa_table_select-", pad=(5, 10), hide_vertical_scroll=True,
                               right_click_menu=['&right_click', ["-report_failure-"]])

        # output_view = sg.Output(size=(150, 5), background_color="white",expand_x=True, key="-output-")

        layout = [
            [self.__facebook__()],
            [filter_column, table_view],
            [layout_button_row],
            [table_view2],
            # [output_view]
        ]

        window = sg.Window('failure mode logger', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True, modal=True)
        window["-Config_Input-"].bind("<Button-1>", "-ConfigPop-")
        window["-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")
        window["-fa_table_select-"].bind("<Return>", "return-")

        return window

    @staticmethod
    def popup_stress_setup():
        layout_filter_column = [
            [sg.Txt("RelStress", size=(15, 1)),
             sg.Combo(["dummyStress1", "dummyStress2"], disabled=False, enable_events=True,
                      key="-rel_stress-", size=(20, 1))],
            [sg.Txt("Checkpoint", size=(15, 1)),
             sg.Listbox(values=["dummyCheckpoint1", "dummyCheckpoint2"], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        size=(20, 10), key="-checkpoint_list-", enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column)

        layout_button_column = [
            [sg.B("Rename Stress", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="each failure mode can only belongs to one group")],
            [sg.B("Create New Checkpoint", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=False, disabled_button_color="#ababab")],
            [sg.B("Archive Checkpoints", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab")],
            [sg.B("Rename Checkpoint", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)

        layout = [
            [filter_column, button_column],
        ]

        window = sg.Window('Setup Stress', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        window["-rel_stress-"].bind("<KeyPress>", "key")
        return window

    @staticmethod
    def popup_config_setup():
        layout_filter_column = [
            [sg.Txt("Program", size=(15, 1)),
             sg.Combo(["program1", "program2"], disabled=False, enable_events=True,
                      key="-program-", size=(20, 1))],
            [sg.Txt("Build", size=(15, 1)),
             sg.Combo(["Build1", "Build2"], disabled=False, enable_events=True,
                      key="-build-", size=(20, 1))],
            [sg.Txt("Config", size=(15, 1)),
             sg.Listbox(values=["dummyCheckpoint1", "dummyCheckpoint2"], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(20, 10), key="-config-", enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column)

        layout_button_column = [
            [sg.B("Rename Program", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="type in program to be renamed then click rename program")],
            [sg.B("Rename Build", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=False, disabled_button_color="#ababab")],
            [sg.B("Create Config", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab")],
            [sg.B("Rename Config", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)

        layout = [
            [filter_column, button_column],
        ]

        window = sg.Window('Setup Config', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        window["-program-"].bind("<KeyPress>", "key")
        window["-build-"].bind("<KeyPress>", "key")
        return window

    def data_log_view(self):
        table_col = ['PK', '   SerialNumber   ', '   Stress   ', '   Checkpoint   ', "  WIP  ", "   Config   ",
                     "   EndTime   "]
        show_heading = [False, True, True, True, True, True, True]
        table_value = [[str(row) for row in range(7)] for _ in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col, select_mode=sg.SELECT_MODE_BROWSE,
                              expand_x=True, num_rows=11, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white",
                              enable_events=True, key="-table_select-", pad=(5, 5), hide_vertical_scroll=True)

        layout_filter_column = [
            [self.__station_name__()],
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-"), sg.In(key="-SN_Input-", enable_events=True)],
            [sg.Txt(text="WIP", size=(15, 1), key="-display_wip-"), sg.In(key="-WIP_Input-", enable_events=True)],
            [sg.Txt("Config", size=(15, 1), key="-display-config"), sg.In("", disabled=True, key="-Config_Input-")],
            [sg.Txt("Current Checkpoint", size=(15, 1), key="-display-ckp"),
             sg.In("", disabled=True, key="-Ckp_Input-")],
            [sg.Txt("Last Checkpoint Only", size=20),
             sg.Rad("T", group_id="table_show_latest", default=False, enable_events=True, key="-show_latest1-"),
             sg.Rad("F", group_id="table_show_latest", default=True, enable_events=True, key="-show_latest0-")],
            [sg.Txt("Current Station Only", size=20),
             sg.Rad("T", group_id="table_show_current_station", default=False, enable_events=True,
                    key="-show_current1-"),
             sg.Rad("F", group_id="table_show_current_station", default=True, enable_events=True,
                    key="-show_current0-")],
        ]

        filter_column = sg.Column(layout=layout_filter_column,
                                  size=(int(300 * rel_tracker_view.scale), int(180 * rel_tracker_view.scale)), )

        button_row = [sg.B("Reset Filter", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           disabled=False, disabled_button_color="#ababab"),
                      sg.B("Start Timer", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           disabled=True, disabled_button_color="#ababab"),
                      sg.B("End Timer", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           disabled=True, disabled_button_color="#ababab"),
                      sg.B("Correct Mistake", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           disabled=True, disabled_button_color="#ababab", tooltip="no available"),
                      sg.B("Offline Tag", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           disabled=False, disabled_button_color="#ababab",
                           tooltip="search input folder and determine which stress and config info the test file "
                                   "belongs to"),
                      ]

        table_col = ['PK', 'SerialNumber', 'WIP', 'Stress', 'Checkpoint', 'folder group',
                     "Notes", "StartTime", "EndTime"]
        show_heading = [False, True, True, True, True, True, True, True, True]
        table_value2 = [[str(row) for row in range(9)] for _ in range(1)]
        table_view2 = sg.Table(values=table_value2, visible_column_map=show_heading,
                               headings=table_col, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                               expand_x=True, num_rows=15, font="Helvetica 12", header_font="Helvetica 10 bold",
                               header_background_color="white",
                               enable_events=True, key="-data_table_select-", pad=(5, 10), hide_vertical_scroll=True)

        # output_view = sg.Output(size=(120, 5), background_color="white",expand_x=True, key="-output-")

        layout = [
            [self.__facebook__()],
            [filter_column, table_view],
            [sg.Rad("Group Tagging", group_id="tagging_flavor",
                    default=False, enable_events=True, key="-tag_group-"),
             sg.Rad("Single Unit Tagging", group_id="tagging_flavor",
                    default=True, enable_events=True, key="-tag_single-"),
             sg.Txt("Folder Name:"), sg.In(default_text="",
                                           tooltip="provide a name if "
                                                   "you need data to be placed in a specific "
                                                   "sub-folder", key="-folder_name-"), ],
            button_row,
            [table_view2]
            # [output_view]
        ]

        window = sg.Window('Data Tagger', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True, modal=True)
        window["-Config_Input-"].bind("<Button-1>", "-ConfigPop-")
        window["-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")

        return window

    @staticmethod
    def failure_mode_summary():
        layout = [
            [sg.Txt("Failure Mode", size=(15, 1)),
             sg.InputText(key="-Failure_Mode_Search-", enable_events=True, size=(30, 1))],
            [sg.Listbox(key="-Failure_Mode_Selection-", values=[],
                        size=(45, 5), enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
            [sg.B("Generate Summary", enable_events=True, size=(15, 1))]
        ]
        window = sg.Window('failure mode selector', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        return window
