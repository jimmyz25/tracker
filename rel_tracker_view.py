import PySimpleGUI as sg


class rel_tracker_view:
    scale = 1
    button_font = "Helvetica 10"
    table_font = "Helvetica 10"
    table_header_font = "Helvetica 10 bold"
    text_font = "Helvetica 10"
    logo_font = 'Helvetica 30 bold'
    station_font = "Helvetica 15 bold"

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
        window = sg.Window('Welcome Page', layout, keep_on_top=True, grab_anywhere=False, no_titlebar=True,
                           finalize=True, auto_close=True, auto_close_duration=1, background_color='#4267B2')
        rel_tracker_view.scale = window["-version-"].get_size()[0] / 249
        print(sg.Window.get_screen_size())
        if sg.Window.get_screen_size()[0] < 1500:
            rel_tracker_view.scale = rel_tracker_view.scale / 1.2
            rel_tracker_view.button_font = "Helvetica 8"
            rel_tracker_view.table_font = "Helvetica 8"
            rel_tracker_view.table_header_font = "Helvetica 8 bold"
            rel_tracker_view.text_font = "Helvetica 8"
            rel_tracker_view.logo_font = 'Helvetica 20 bold'
            rel_tracker_view.station_font = "Helvetica 9 bold"
        elif sg.Window.get_screen_size()[0] < 2500:
            rel_tracker_view.scale = rel_tracker_view.scale / 1
            rel_tracker_view.button_font = "Helvetica 12"
            rel_tracker_view.table_font = "Helvetica 12"
            rel_tracker_view.table_header_font = "Helvetica 12 bold"
            rel_tracker_view.text_font = "Helvetica 12"
            rel_tracker_view.logo_font = 'Helvetica 25 bold'
            rel_tracker_view.station_font = "Helvetica 15 bold"
        else:
            rel_tracker_view.scale = rel_tracker_view.scale / 1
            rel_tracker_view.button_font = "Helvetica 10"
            rel_tracker_view.table_font = "Helvetica 10"
            rel_tracker_view.table_header_font = "Helvetica 10 bold"
            rel_tracker_view.text_font = "Helvetica 10"
            rel_tracker_view.logo_font = 'Helvetica 30 bold'
            rel_tracker_view.station_font = "Helvetica 15 bold"
        # print(sg.Window.get_screen_dimensions())
        return window

    @staticmethod
    def __facebook__():
        facebook_text = sg.Txt("Meta", border_width=0, text_color="#4267B2", font=rel_tracker_view.logo_font,
                               justification='center', pad=5, key="-Home-", enable_events=True)
        column1 = sg.Column(layout=[[facebook_text]],
                            size=(int(600 * rel_tracker_view.scale), int(40 * rel_tracker_view.scale)))

        return [
            [column1, sg.Stretch(),
             sg.Txt("Meta RL project only", font='Helvetica 10', text_color='#4267B2', size=(18, 1))]]

    @staticmethod
    def __station_name__():
        text = sg.Txt("Station", text_color="Black", font=rel_tracker_view.station_font, key="-station_name-"
                      )
        return text

    @staticmethod
    def preference_view():
        layout1 = [
            [sg.Txt("Station Name", size=15, font=rel_tracker_view.text_font),
             sg.InputText(size=30, font=rel_tracker_view.text_font,
                          key="-Station_Name-", tooltip="maximum character: 18"), sg.Stretch(),
             ],
            [sg.Txt("Station Type", size=15, font=rel_tracker_view.text_font),
             sg.Combo(values=[], size=30, readonly=True, font=rel_tracker_view.text_font, key="-station-type-",
                      enable_events=True),
             sg.B("Go", font=rel_tracker_view.button_font),
             sg.Stretch(),
             ],
            [sg.HorizontalSeparator()],
            [sg.Txt("data tagging station settings:", font=rel_tracker_view.text_font)],
            [sg.Txt("Input Folder", size=15, font=rel_tracker_view.text_font),
             sg.InputText(size=30, readonly=True,
                          font=rel_tracker_view.text_font, key="-Input_Folder-"), sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), font=rel_tracker_view.text_font,
                             tooltip="Input folder where data will be saved before tagging",
                             target=(sg.ThisRow, -2), key="input_folder_browse", disabled=False)],
            [sg.Txt("Output Folder", size=15,
                    font=rel_tracker_view.text_font),
             sg.InputText(size=30, readonly=True, key="-Output_Folder-",
                          font=rel_tracker_view.text_font),
             sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), target=(sg.ThisRow, -2), font=rel_tracker_view.text_font,
                             key="output_folder_browse", disabled=False, )],
            [sg.HorizontalSeparator()],
            [sg.Txt("Golden Database", size=15, font=rel_tracker_view.text_font
                    ), sg.InputText(size=30, font=rel_tracker_view.text_font,
                                    readonly=True,
                                    key="-Golden_Database-", enable_events=True),
             sg.Stretch(),
             sg.FileBrowse(size=(10, 1),
                           font=rel_tracker_view.text_font,
                           target=(sg.ThisRow, -2), key="-add_golden_address-", enable_events=True)],
            [sg.Txt("Local Database", size=15, font=rel_tracker_view.text_font),
             sg.InputText(size=30, readonly=True,
                          key="-Local_Database-", font=rel_tracker_view.text_font,
                          enable_events=True),
             sg.Stretch(),
             sg.FileBrowse(size=(10, 1), font=rel_tracker_view.text_font,
                           target=(sg.ThisRow, -2)), ],
            [sg.Btn("Configs Setup", size=15, font=rel_tracker_view.button_font),
             sg.Btn("Stress Setup", size=15, font=rel_tracker_view.button_font)],
            [sg.Btn("Save Preference", size=15, font=rel_tracker_view.button_font),
             sg.Btn("Sync with Golden", size=15, font=rel_tracker_view.button_font)]
        ]

        window = sg.Window('Preference', layout1, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True)
        return window

    def rel_lab_station_view(self):
        tab_new_left = [
            [sg.Txt(text="WIP", size=(15, 1),
                    font=rel_tracker_view.text_font),
             sg.In(key="-New-WIP_Input-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Txt("Assign Config", size=(15, 1), font=rel_tracker_view.text_font),
             sg.In(key="-New-Config_Input-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Txt("initial Checkpoint", size=(15, 1), font=rel_tracker_view.text_font),
             sg.In(key="-New-Ckp_Input-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Txt("Notes", size=(15, 1), font=rel_tracker_view.text_font),
             sg.In(key="-New-Note-", enable_events=False, font=rel_tracker_view.text_font)],
            [sg.Txt("SerialNumber (0)", size=(15, 3),
                    expand_y=True, key="-Multi_SN-", font=rel_tracker_view.text_font),
             sg.Multiline(size=(40, 3), expand_y=True, no_scrollbar=True, enable_events=False, key="-New-SN_Input-",
                          font=rel_tracker_view.text_font,
                          tooltip="copy paste from csv or manually enter, finish with RETURN \n Note:duplicates will "
                                  "be removed ")]
        ]
        tab1 = sg.Tab(layout=tab_new_left, title="Register New Unit")

        tab_old_left = [
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-", font=rel_tracker_view.text_font),
             sg.In(key="-SN_Input-", enable_events=True)],
            [sg.Txt(text="WIP", size=(15, 1), key="-display_wip-", font=rel_tracker_view.text_font),
             sg.In(key="-WIP_Input-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Txt("Config", size=(15, 1), key="-display-config", font=rel_tracker_view.text_font),
             sg.In("", disabled=True, key="-Config_Input-", font=rel_tracker_view.text_font)],
            [sg.Txt("Current Checkpoint", size=(15, 1), key="-display-ckp", font=rel_tracker_view.text_font),
             sg.In("", disabled=True, key="-Ckp_Input-", font=rel_tracker_view.text_font)],
            [sg.Txt("Notes", size=(15, 3), expand_y=True, font=rel_tracker_view.text_font),
             sg.Multiline(size=(40, 3), expand_y=True, font=rel_tracker_view.text_font,
                          no_scrollbar=True, key="-Note-")]
        ]

        tab2 = sg.Tab(layout=tab_old_left, title="Existing Units")

        tab_group = sg.TabGroup(layout=[[tab1, tab2]],
                                size=(int(350 * rel_tracker_view.scale), int(180 * rel_tracker_view.scale)),
                                enable_events=True, key="-Tab_Selection-")

        layout_button_column = [
            [self.__station_name__()],
            [sg.B("Add", size=(15, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  font=rel_tracker_view.button_font,
                  tooltip="register new units in batch",
                  ),
             sg.B("Assign WIP", size=(15, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  font=rel_tracker_view.button_font,
                  tooltip="select or enter existing units then fill in WIP in 'register new unit' tab "),
             ],
            [sg.B("Reset", size=(15, 1), pad=(5, 2),
                  disabled=False, disabled_button_color="#ababab",
                  font=rel_tracker_view.button_font,
                  tooltip="reset filter"),
             sg.B("Update", size=(15, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  font=rel_tracker_view.button_font,
                  tooltip="only available in update mode")],
            [sg.B("CheckIn", size=(15, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  font=rel_tracker_view.button_font,
                  tooltip="check in selected units to new checkpoints \n"
                          "Note: only available to latest status row"),
             sg.B("Checkout", size=(15, 1), pad=(5, 2),
                  disabled=True, disabled_button_color="#ababab",
                  font=rel_tracker_view.button_font,
                  tooltip="checkout current checkpoint to indicate completion of checkpoint")
             ],
            [sg.B("Delete", size=(15, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  disabled=True, disabled_button_color="#ababab"),
             sg.B("Add Dummy SN", size=(15, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="only for demo, disabled for normal use")
             ],
            [sg.B("Remove for FA", size=(15, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="assign selected row to WIP: 'FA' "),
             sg.B("Show Summary", size=(15, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="generate a summary to show test status")
             ],

        ]
        button_column = sg.Column(layout=layout_button_column,
                                  size=(int(350 * rel_tracker_view.scale), int(200 * rel_tracker_view.scale)))

        table_col = ['PK', 'Config', 'WIP', 'SerialNumber', 'Stress', 'Checkpoint', 'Start', 'End',
                     'Note']
        show_heading = [False, True, True, True, True, True, True, True, True]
        table_value = [[str(row) for row in range(9)] for _ in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col, select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                              expand_x=True, num_rows=15, font=rel_tracker_view.table_font,
                              header_font=rel_tracker_view.table_header_font,
                              header_background_color="white",
                              right_click_menu=['&right_click', ["Enter Update Mode", "Exit Update Mode"]],
                              enable_events=True, key="-table_select-", pad=(5, 10), hide_vertical_scroll=False)
        output_view = sg.Output(size=(145, 5), background_color="white", expand_x=True, key="-output-",
                                font=rel_tracker_view.text_font)
        layout_status_column = [
            [
                sg.Rad("Latest record", group_id="table_show_latest", default=False,
                       enable_events=True, font=rel_tracker_view.text_font,
                       key="-show_latest1-"),
                sg.Rad("All record", group_id="table_show_latest", font=rel_tracker_view.text_font,
                       default=True, enable_events=True, key="-show_latest0-")],

            [sg.Rad("Self Station", font=rel_tracker_view.text_font,
                    group_id="table_show_current_station",
                    default=False, enable_events=True, key="-show_current1-"),
             sg.Rad("All Stations", font=rel_tracker_view.text_font,
                    group_id="table_show_current_station",
                    default=True, enable_events=True, key="-show_current0-")],
            [sg.B("Daily Report", size=(15, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  disabled=False, disabled_button_color="#ababab",
                  )]
        ]
        status_column = sg.Column(layout=layout_status_column,
                                  size=(int(250 * rel_tracker_view.scale), int(150 * rel_tracker_view.scale)),
                                  key="-status-column")
        layout = [
            [self.__facebook__()],
            [tab_group, button_column, status_column, sg.Stretch()],
            [table_view],
            [output_view]
        ]

        window = sg.Window('Rel Status Logger', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
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
            [sg.Txt("Program", size=15, font=rel_tracker_view.text_font),
             sg.InputCombo(size=30, font=rel_tracker_view.text_font,
                           values=[], key="Program", enable_events=True), sg.Stretch(),
             ],
            [sg.Txt("Build", font=rel_tracker_view.text_font, size=15),
             sg.InputCombo(values=[], size=30, readonly=True, font=rel_tracker_view.text_font,
                           key="Build", enable_events=True), sg.Stretch()],
            [sg.Txt("Config", size=15, font=rel_tracker_view.text_font),
             sg.InputCombo(values=[],
                           size=30, readonly=True, font=rel_tracker_view.text_font,
                           key="Config", enable_events=True), sg.Stretch()],
            [sg.B("Save and Close", enable_events=True, key="-Save-", font=rel_tracker_view.button_font, size=(25, 1)),
             sg.B("Clear", enable_events=True, key="-Clear-", font=rel_tracker_view.button_font)]

        ]

        window = sg.Window('Config Selection', layout1, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, modal=True)
        window["Program"].bind("<KeyPress>", "-KeyPress")
        # window.TKroot.grab_set()

        return window

    @staticmethod
    def popup_stress_select():
        layout1 = [
            [sg.Txt("RelStress", size=15, font=rel_tracker_view.text_font),
             sg.InputCombo(size=30, font=rel_tracker_view.text_font, values=[], key="RelStress", enable_events=True),
             sg.Stretch()],
            [sg.Txt("RelCheckpoint", size=15, font=rel_tracker_view.text_font),
             sg.InputCombo(values=[], size=30, readonly=True,
                           key="RelCheckpoint", enable_events=True), sg.Stretch()],
            [sg.B("Save and Close", font=rel_tracker_view.text_font, enable_events=True, key="-Save-", size=(25, 1)),
             sg.B("Clear", font=rel_tracker_view.text_font, enable_events=True, key="-Clear-")]

        ]

        window = sg.Window('Stress Selection', layout1, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
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
            [sg.B("Add >>>", size=(10, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, key="-Add-", disabled_button_color="#ababab")],
            [sg.B("Remove <<<", size=(10, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, key="-Remove-", disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)
        table_col = ['PK', 'failure mode set', '     failure mode     ', '     detail     ']
        show_heading = [False, True, True, True]
        table_value = [[str(row) for row in range(4)] for _ in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col, size=(40, 10),
                              expand_x=True, num_rows=12, font=rel_tracker_view.table_font,
                              header_font=rel_tracker_view.table_header_font,
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
                  disabled=True, font=rel_tracker_view.button_font,
                  disabled_button_color="#ababab")],
            [sg.Multiline(default_text="", size=(40, 15), expand_x=True, key="-fa-detail-")]
        ]

        window = sg.Window('Update Failure Mode', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
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
            [sg.B("Group Failure Modes", size=(20, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab",
                  tooltip="each failure mode can only belongs to one group")],
            [sg.B("Create New Failure Mode", size=(20, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=False, disabled_button_color="#ababab")],
            [sg.B("Archive Failure Mode", size=(20, 1), pad=(5, 2),
                  font=rel_tracker_view.button_font,
                  mouseover_colors=("#0f3948", "#a8d8eb"),
                  disabled=True, disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)

        layout = [
            [filter_column, button_column],
        ]

        window = sg.Window('Config Failure Mode', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        return window

    def fa_log_view(self):
        table_col = ['PK', '   SerialNumber   ', '   Stress   ', '   Checkpoint   ', "   Config   ", "   EndTime   "]
        show_heading = [False, True, True, True, True, True]
        table_value = [[str(row) for row in range(6)] for _ in range(1)]
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col, select_mode=sg.SELECT_MODE_BROWSE,
                              expand_x=True, num_rows=11, font=rel_tracker_view.table_font,
                              header_font=rel_tracker_view.table_header_font,
                              header_background_color="white", expand_y=True,
                              enable_events=True, key="-table_select-", pad=(5, 5), hide_vertical_scroll=True)

        layout_filter_column = [
            [self.__station_name__()],
            [
                sg.Rad("Latest record", group_id="table_show_latest", default=False,
                       enable_events=True, font=rel_tracker_view.text_font,
                       key="-show_latest1-"),
                sg.Rad("All record", group_id="table_show_latest", font=rel_tracker_view.text_font,
                       default=True, enable_events=True, key="-show_latest0-")],

            [sg.Rad("Self Station", font=rel_tracker_view.text_font,
                    group_id="table_show_current_station",
                    default=False, enable_events=True, key="-show_current1-"),
             sg.Rad("All Stations", font=rel_tracker_view.text_font,
                    group_id="table_show_current_station",
                    default=True, enable_events=True, key="-show_current0-")],
            [sg.Txt("SerialNumber", size=(15, 1), font=rel_tracker_view.text_font),
             sg.In(key="-SN_Input-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Txt(text="WIP", font=rel_tracker_view.text_font, size=(15, 1)),
             sg.In(key="-WIP_Input-", font=rel_tracker_view.text_font, enable_events=True)],
            [sg.Txt("Config", font=rel_tracker_view.text_font, size=(15, 1), key="-display-config"),
             sg.In("", disabled=True, font=rel_tracker_view.text_font, key="-Config_Input-")],
            [sg.Txt("Current Checkpoint", font=rel_tracker_view.text_font, size=(15, 1), key="-display-ckp"),
             sg.In("", disabled=True, font=rel_tracker_view.text_font, key="-Ckp_Input-")],
            [sg.Txt("Failure Mode", font=rel_tracker_view.text_font, size=(15, 1)),
             sg.In("", disabled=False, font=rel_tracker_view.text_font, key="-Failure_Mode_Input-",
                   enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column,
                                  size=(int(330 * rel_tracker_view.scale), int(220 * rel_tracker_view.scale)), )

        layout_button_row = [
            sg.B("Reset Filter", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                 font=rel_tracker_view.button_font,
                 disabled=False, disabled_button_color="#ababab"),
            sg.B("Edit Failure Modes", size=(25, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                 font=rel_tracker_view.button_font,
                 disabled=False, disabled_button_color="#ababab"),
            sg.B("Report Failure", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                 font=rel_tracker_view.button_font,
                 disabled=True, disabled_button_color="#ababab"),
            sg.B("Show Summary", size=(20, 1), pad=(5, 2),
                 font=rel_tracker_view.button_font,
                 disabled=False, disabled_button_color="#ababab"),
            sg.B("Distribution Fitting", enable_events=True, font=rel_tracker_view.button_font, size=(15, 1))
        ]

        table_col = ['PK', 'Failure Group', 'Failure Mode', 'SerialNumber', 'Stress', 'Checkpoint', 'DateAdded',
                     "Detail"]
        show_heading = [False, True, True, True, True, True, True, True]
        table_value2 = [[str(row) for row in range(8)] for _ in range(1)]
        table_view2 = sg.Table(values=table_value2, visible_column_map=show_heading,
                               headings=table_col, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                               expand_x=True, num_rows=15, font=rel_tracker_view.table_font,
                               header_font=rel_tracker_view.table_header_font,
                               header_background_color="white", expand_y=True,
                               enable_events=True, key="-fa_table_select-", pad=(5, 10), hide_vertical_scroll=True,
                               right_click_menu=['&right_click', ["update failure"]])

        output_view = sg.Output(size=(145, 5),
                                font=rel_tracker_view.text_font,
                                background_color="white", expand_x=True, key="-output-")

        layout = [
            [self.__facebook__()],
            [filter_column, table_view],
            [layout_button_row],
            [table_view2],
            [output_view]
        ]

        window = sg.Window('failure mode logger', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
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
                  font=rel_tracker_view.button_font,
                  tooltip="each failure mode can only belongs to one group")],
            [sg.B("Create New Checkpoint", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  font=rel_tracker_view.button_font,
                  disabled=False, disabled_button_color="#ababab")],
            [sg.B("Archive Checkpoints", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  font=rel_tracker_view.button_font,
                  disabled=True, disabled_button_color="#ababab")],
            [sg.B("Rename Checkpoint", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  font=rel_tracker_view.button_font,
                  disabled=True, disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)

        layout = [
            [filter_column, button_column],
        ]

        window = sg.Window('Setup Stress', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        window["-rel_stress-"].bind("<KeyPress>", "key")
        return window

    @staticmethod
    def popup_config_setup():
        layout_filter_column = [
            [sg.Txt("Program", size=(15, 1), font=rel_tracker_view.text_font),
             sg.Combo(["program1", "program2"], font=rel_tracker_view.text_font, disabled=False, enable_events=True,
                      key="-program-", size=(20, 1))],
            [sg.Txt("Build", size=(15, 1), font=rel_tracker_view.text_font),
             sg.Combo(["Build1", "Build2"], font=rel_tracker_view.text_font, disabled=False, enable_events=True,
                      key="-build-", size=(20, 1))],
            [sg.Txt("Config", size=(15, 1), font=rel_tracker_view.text_font),
             sg.Listbox(values=["dummyCheckpoint1", "dummyCheckpoint2"], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(20, 10), key="-config-", font=rel_tracker_view.text_font, enable_events=True)],
        ]

        filter_column = sg.Column(layout=layout_filter_column)

        layout_button_column = [
            [sg.B("Rename Program", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  font=rel_tracker_view.button_font,
                  disabled=False, disabled_button_color="#ababab",
                  tooltip="type in program to be renamed then click rename program")],
            [sg.B("Rename Build", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  font=rel_tracker_view.button_font,
                  disabled=False, disabled_button_color="#ababab")],
            [sg.B("Create Config", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  font=rel_tracker_view.button_font,
                  disabled=True, disabled_button_color="#ababab")],
            [sg.B("Rename Config", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                  font=rel_tracker_view.button_font,
                  disabled=True, disabled_button_color="#ababab")],
        ]
        button_column = sg.Column(layout=layout_button_column, expand_y=True)

        layout = [
            [filter_column, button_column],
        ]

        window = sg.Window('Setup Config', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
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
                              headings=table_col, select_mode=sg.SELECT_MODE_EXTENDED,
                              expand_x=True, num_rows=11, font=rel_tracker_view.table_font,
                              header_font=rel_tracker_view.table_header_font,
                              header_background_color="white",
                              enable_events=True, key="-table_select-", pad=(5, 5), hide_vertical_scroll=True)

        layout_filter_column = [
            [self.__station_name__()],
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-", font=rel_tracker_view.text_font),
             sg.In(key="-SN_Input-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Txt(text="WIP", size=(15, 1), key="-display_wip-", font=rel_tracker_view.text_font),
             sg.In(key="-WIP_Input-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Txt("Config", size=(15, 1), font=rel_tracker_view.text_font, key="-display-config"),
             sg.In("", disabled=True, key="-Config_Input-", font=rel_tracker_view.text_font)],
            [sg.Txt("Current Checkpoint", size=(15, 1), key="-display-ckp", font=rel_tracker_view.text_font),
             sg.In("", disabled=True, key="-Ckp_Input-", font=rel_tracker_view.text_font)],
            [
                sg.Rad("Latest record", group_id="table_show_latest", default=False,
                       enable_events=True, font=rel_tracker_view.text_font,
                       key="-show_latest1-"),
                sg.Rad("All record", group_id="table_show_latest", font=rel_tracker_view.text_font,
                       default=True, enable_events=True, key="-show_latest0-")],

            [sg.Rad("Self Station", font=rel_tracker_view.text_font,
                    group_id="table_show_current_station",
                    default=False, enable_events=True, key="-show_current1-"),
             sg.Rad("All Stations", font=rel_tracker_view.text_font,
                    group_id="table_show_current_station",
                    default=True, enable_events=True, key="-show_current0-")],
        ]

        filter_column = sg.Column(layout=layout_filter_column,
                                  size=(int(300 * rel_tracker_view.scale), int(200 * rel_tracker_view.scale)), )

        button_row = [sg.B("Reset Filter", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           font=rel_tracker_view.button_font,
                           disabled=False, disabled_button_color="#ababab"),
                      sg.B("Start Timer", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           font=rel_tracker_view.button_font,
                           disabled=True, disabled_button_color="#ababab"),
                      sg.B("End Timer", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           font=rel_tracker_view.button_font,
                           disabled=True, disabled_button_color="#ababab"),
                      sg.B("Offline Tag", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           font=rel_tracker_view.button_font,
                           disabled=False, disabled_button_color="#ababab",
                           tooltip="search input folder and determine which stress and config info the test file "
                                   "belongs to"),
                      sg.B("Delete", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           font=rel_tracker_view.button_font,
                           disabled=True, disabled_button_color="#ababab"),
                      sg.B("CSV Compiler", size=(20, 1), pad=(5, 2), mouseover_colors=("#0f3948", "#a8d8eb"),
                           font=rel_tracker_view.button_font,
                           disabled=False, disabled_button_color="#ababab"),
                      ]

        table_col = ['PK', 'SerialNumber', 'WIP', 'Stress', 'Checkpoint', 'Test Station',
                     "Notes", "StartTime", "EndTime"]
        show_heading = [False, True, True, True, True, True, True, True, True]
        table_value2 = [[str(row) for row in range(9)] for _ in range(1)]
        table_view2 = sg.Table(values=table_value2, visible_column_map=show_heading,
                               headings=table_col, select_mode=sg.SELECT_MODE_EXTENDED,
                               expand_x=True, num_rows=15, font=rel_tracker_view.table_font,
                               header_font=rel_tracker_view.table_header_font,
                               header_background_color="white",
                               enable_events=True, key="-data_table_select-", pad=(5, 10), hide_vertical_scroll=True)

        output_view = sg.Output(size=(145, 5), font=rel_tracker_view.text_font,
                                background_color="white", expand_x=True, key="-output-")

        layout = [
            [self.__facebook__()],
            [filter_column, table_view],
            [
             #    sg.Rad("Group Tagging", group_id="tagging_flavor", font=rel_tracker_view.text_font,
             #        default=False, enable_events=True, key="-tag_group-"),
             # sg.Rad("Single Unit Tagging", group_id="tagging_flavor", font=rel_tracker_view.text_font,
             #        default=True, enable_events=True, key="-tag_single-"),
             sg.Txt("Parametric Station Name:", font=rel_tracker_view.text_font),
             sg.In(default_text="",
                   tooltip="tester name or test stationID",
                   key="-folder_name-"), ],
            button_row,
            [table_view2],
            [output_view]
        ]

        window = sg.Window('Parametric Testing Station', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=True, modal=False)
        window["-Config_Input-"].bind("<Button-1>", "-ConfigPop-")
        window["-Ckp_Input-"].bind("<Button-1>", "-CkpPop-")

        return window

    @staticmethod
    def failure_mode_summary():
        layout = [
            [sg.Txt("Failure Mode", size=(15, 1), font=rel_tracker_view.text_font),
             sg.InputText(key="-Failure_Mode_Search-", font=rel_tracker_view.text_font,
                          enable_events=True, size=(30, 1))],
            [sg.Listbox(key="-Failure_Mode_Selection-", values=[], font=rel_tracker_view.text_font,
                        size=(45, 5), enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
            [sg.B("Generate Summary", enable_events=True, font=rel_tracker_view.button_font, size=(15, 1))]
        ]
        window = sg.Window('failure mode selector', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        return window

    @staticmethod
    def file_view():
        table_col = ["   " + str(i) + "   " for i in range(10)]
        table_value = [["" for _ in range(10)] for _ in range(1)]
        table_view = sg.Table(values=table_value,
                              headings=table_col, select_mode=sg.TABLE_SELECT_MODE_NONE,
                              expand_x=True, num_rows=17, font=rel_tracker_view.table_font,
                              header_font=rel_tracker_view.table_header_font,
                              header_background_color="white",
                              enable_events=True, key="-file_preview_window-", pad=(5, 5), hide_vertical_scroll=True)

        table2_col = ["filename"]
        table2_value = [["" for _ in range(10)] for _ in range(1)]
        table2_view = sg.Table(values=table2_value,
                               headings=table2_col, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                               expand_x=True, num_rows=20, font=rel_tracker_view.table_font,
                               header_font=rel_tracker_view.table_header_font,
                               header_background_color="white",
                               enable_events=True, key="-folder_preview_window-", pad=(5, 5), hide_vertical_scroll=True)

        setting_col_layout = [
            [sg.Txt("encode", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Combo(values=[], size=15, key="encode", font=rel_tracker_view.text_font)],
            [sg.Txt("start_row", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Spin(values=[i for i in range(10)], size=15, key="start_row", font=rel_tracker_view.text_font)],
            [sg.Txt("timestamp_col", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Combo(values=[], size=15, key="start_time", font=rel_tracker_view.text_font)],
            [sg.Txt("serial_number_col", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Combo(values=[], size=15, key="serial_number", font=rel_tracker_view.text_font)],
            [sg.Txt("delimiter", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Combo(values=[], size=15, key="separator", font=rel_tracker_view.text_font)],
            [sg.Txt("skip_keywords", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Input(size=15, key="skip_keywords", font=rel_tracker_view.text_font, tooltip="separated by ; ")],
            [sg.Txt("skip_rows", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Input(size=15, key="skip_rows", font=rel_tracker_view.text_font, tooltip="separated by ;")],
            [sg.Txt("timestamp format", font=rel_tracker_view.text_font), sg.Stretch(),
             sg.Combo(values=['%Y%m%d-%H%M%S', "%Y/%m/%d %H:%M:%S"],
                      key="timestamp_format", size=20, font=rel_tracker_view.text_font)],
            [sg.B("Regen Preview", font=rel_tracker_view.text_font)]
        ]
        setting_col = sg.Column(setting_col_layout)

        layout1 = [
            [sg.Txt("data tagging station settings:", font=rel_tracker_view.text_font)],
            [sg.Txt("File Preview", font=rel_tracker_view.text_font, size=15),
             sg.InputText(size=30, readonly=True,
                          font=rel_tracker_view.text_font, key="-Preview-"), sg.Stretch(),
             sg.FileBrowse(size=(10, 1), enable_events=True, font=rel_tracker_view.text_font,
                           target=(sg.ThisRow, -2), disabled=False),
             sg.B("Open File", font=rel_tracker_view.text_font)],
            [sg.HorizontalSeparator()],
            [table_view, setting_col],
            [sg.Txt("Directory Path", size=15, font=rel_tracker_view.text_font),
             sg.InputText(size=30, readonly=True,
                          font=rel_tracker_view.text_font, key="-Folder_to_Scan-", enable_events=True),
             sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), target=(sg.ThisRow, -2), disabled=False, font=rel_tracker_view.text_font),
             sg.B("Scan Folder", font=rel_tracker_view.text_font)],
            [sg.HorizontalSeparator()],
            [table2_view],
            [sg.B("Decode and Combine", font=rel_tracker_view.text_font),
             sg.B("Decode Selected", font=rel_tracker_view.text_font)],
        ]

        window = sg.Window('CSV Compiler', layout1, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        return window

    @staticmethod
    def fitting_view():
        config_table_heading = ["PK", "Program", "Build", "Config", "Group"]
        config_table_value = [["" for _ in range(5)]]
        config_table_show = [False, True, True, True, True]
        config_col_layout = [
            [sg.Text("Config Selection and Grouping", font=rel_tracker_view.text_font)],
            [sg.Table(values=config_table_value, headings=config_table_heading, visible_column_map=config_table_show,
                      font=rel_tracker_view.table_font, header_font=rel_tracker_view.table_header_font,
                      num_rows=10, key="-config_table-")],
            [sg.Button("Update Grouping", font=rel_tracker_view.button_font)]
        ]
        config_table_col = sg.Column(layout=config_col_layout)

        stress_table_heading = ["PK", "RelStresss", "RelCheckpoint", "Value", "P_A", "P_B"]
        stress_table_value = [["" for _ in range(6)]]
        stress_table_show = [False, True, True, True, True, True]
        stress_col_layout = [
            [sg.Text("Stress Selection", font=rel_tracker_view.text_font)],
            [sg.Table(values=stress_table_value, headings=stress_table_heading, visible_column_map=stress_table_show,
                      font=rel_tracker_view.table_font, header_font=rel_tracker_view.table_header_font,
                      num_rows=10, key="-stress_table-", expand_x=True)],
            [sg.Button("Update Checkpoint Value", font=rel_tracker_view.button_font),
             sg.Button("Assign Parameter A", font=rel_tracker_view.button_font),
             sg.Button("Assign Parameter B", font=rel_tracker_view.button_font)]
        ]
        stress_table_col = sg.Column(layout=stress_col_layout)
        failure_mode_col_layout = [
            [sg.Txt("Failure Mode Sets", size=(15, 1), font=rel_tracker_view.text_font),
             sg.Combo(["cosmetic inspection set 1", "cosmetic inspection set 2"],
                      disabled=False, font=rel_tracker_view.text_font,
                      key="-failure_mode_set-", size=(20, 1), enable_events=True)],
            [sg.Txt("Failure Mode", size=(15, 1), font=rel_tracker_view.text_font),
             sg.Listbox(values=[None], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        size=(20, 11), key="-failure_to_select-", enable_events=True, font=rel_tracker_view.text_font)],
            [sg.Button("Update Data Table", font=rel_tracker_view.button_font,
                       disabled_button_color="#ababab", disabled=True)]
        ]

        failure_mode_table_col = sg.Column(layout=failure_mode_col_layout)

        data_table_heading = ["SN", "T1", "T2", "Group"]
        data_table_value = [["" for _ in range(4)]]
        data_table_show = [True, True, True, True]
        data_col_layout = [
            [sg.Text("Data for distribution fitting", font=rel_tracker_view.text_font)],
            [sg.Table(values=data_table_value, headings=data_table_heading,
                      visible_column_map=data_table_show,
                      font=rel_tracker_view.table_font, header_font=rel_tracker_view.table_header_font,
                      num_rows=10, expand_x=True)],
            [sg.Button("output for JMP", font=rel_tracker_view.button_font),
             sg.Button("output for Relisoft", font=rel_tracker_view.button_font),
             sg.Button("Just Plot here", font=rel_tracker_view.button_font), ]
        ]

        layout = [
            [config_table_col, stress_table_col, failure_mode_table_col],
            [data_col_layout]
        ]

        window = sg.Window('distribution fitting', layout, keep_on_top=False, grab_anywhere=False, no_titlebar=False,
                           finalize=True, enable_close_attempted_event=False, modal=True)
        return window
