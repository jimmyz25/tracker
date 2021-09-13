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
                           finalize=True, auto_close=True, auto_close_duration=5, background_color='#4267B2')
        return window

    @staticmethod
    def __facebook__():
        facebook_text = sg.Txt("facebook", border_width=0, text_color="orange", font='Helvetica 30 bold',
                               justification='center', pad=5, key="-Home-", enable_events=True)
        column1 = sg.Column(layout=[[facebook_text]], size=(600, 40))

        return [
            [column1, sg.Stretch(), sg.Txt("FRL project only", font='Heletica 10', text_color='#4267B2', size=(15, 1))]]

    def preference_view(self):
        layout1 = [
            [sg.Txt("Station Name", size=15),
             sg.InputText(default_text=self.default_settings.get('-station-', ''), size=30,
                          key="-Station_Name-"), sg.Stretch(),
             sg.B("Validate", size=10)],
            [sg.Txt("Station Type", size=15), sg.DropDown(values=["a", "b"], size=30, readonly=True), sg.Stretch(),
             sg.B("Set", size=10)],
            [sg.HorizontalSeparator()],
            [sg.Txt("Input Folder", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), tooltip="abcasdfasdf", target=(sg.ThisRow, -2))],
            [sg.Txt("Output Folder", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FolderBrowse(size=(10, 1), target=(sg.ThisRow, -2))],
            [sg.HorizontalSeparator()],
            [sg.Txt("Golden Database", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FileBrowse(size=(10, 1), target=(sg.ThisRow, -2))],
            [sg.Txt("Auto Sync", size=15), sg.Rad("ON", group_id="auto_sync"), sg.Rad("OFF", group_id="auto_sync")],
            [sg.Btn("Save Preference", size=15), sg.Btn("New Window", key="-New_Window-")]
        ]

        window = sg.Window('Preference', layout1, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True)
        return window

    def rel_lab_station_view(self):
        tab_new_left = [
            [sg.Txt(text="WIP", size=(15, 1)), sg.In()],
            [sg.Txt("Assign Config", size=(15, 1)), sg.In()],
            [sg.Txt("initial Checkpoint", size=(15, 1)), sg.In()],
            [sg.Txt("SerialNumber", size=(15, 3), expand_y=True),
             sg.Multiline(size=(40, 3), expand_y=True, no_scrollbar=True)]
        ]
        # new_tab_combined = [sg.Col(tab_new_left,size=(400,200)),sg.Col(tab_new_right,size=(400,200))]
        tab1 = sg.Tab(layout=tab_new_left, title="Registor New Unit",disabled=True)

        tab_old_left = [
            [sg.Txt("SerialNumber", size=(15, 1), key="-old_sn-"), sg.In(key="ab")],
            [sg.Txt(text="WIP", size=(15, 1), key="-display_wip-"), sg.In(key="a", size=(40, 1))],
            [sg.Txt("Config", size=(15, 1), key="-display-config"), sg.In("", key="ad", size=(40, 1))],
            [sg.Txt("Current Checkpoint", size=(15, 1), key="-display-ckp"), sg.In("", key="add", size=(40, 1))],
            [sg.Txt("Notes", size=(15, 3), expand_y=True, key="-add-note"),
             sg.Multiline(size=(40, 3), expand_y=True, no_scrollbar=True, key="ad33")]
        ]

        tab2 = sg.Tab(layout=tab_old_left, title="Existing Units")

        tab_group = sg.TabGroup(layout=[[tab1, tab2]], size=(400, 150))

        layout_status_column = [
            [sg.Txt("Station", text_color="Black", font='Helvetica 22 bold')],
            [sg.Txt("Last Sync: 24min ago")],
            [sg.Txt("Unit not in Sync:")],
            [sg.VStretch()]
        ]
        status_column = sg.Column(layout=layout_status_column, size=(200, 150))
        layout_button_column = [
            [sg.B("A Record", size=(10, 1), pad=(5, 2), disabled_button_color="grey",enable_events=True),

             sg.B("B Record", size=(10, 1), pad=(5, 2))],
            [sg.B("C Record", size=(10, 1), pad=(5, 2)), sg.B("D Record", size=(10, 1), pad=(5, 2))],
            [sg.B("E Record", size=(10, 1), pad=(5, 2)), sg.B("F Record", size=(10, 1), pad=(5, 2))],
            [sg.B("G Record", size=(10, 1), pad=(5, 2)), sg.B("H Record", size=(10, 1), pad=(5, 2))],
            [sg.B("I Record", size=(10, 1), pad=(5, 2)), sg.B("G Record", size=(10, 1), pad=(5, 2))],
        ]
        button_column = sg.Column(layout=layout_button_column, size=(200, 150))
        table_view = sg.Table(values=[[str(row) for row in range(8)] for col in range(150)],
                              headings=['Config', 'WIP', 'SerialNumber', 'Stress', 'Checkpoint', 'Start', 'End',
                                        'Note'],
                              expand_x=True, num_rows=20, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white", right_click_menu=['&right_click', ["update", "remove"]]
                              , enable_events=True, key="-table_select-", pad=(5, 10), hide_vertical_scroll=True)
        layout = [
            [self.__facebook__()],
            [tab_group, button_column, status_column, sg.Stretch()],
            [table_view]
        ]

        window = sg.Window('Rel Status Logger', layout, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True)
        return window
