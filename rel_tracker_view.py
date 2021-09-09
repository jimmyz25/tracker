import PySimpleGUI as sg


class rel_tracker_view:
    def __init__(self, settings: sg.user_settings):
        self.default_settings = settings

    def __facebook__(self):
        return [sg.Txt("Facebook", size=(20, 1), font=("Helvetica", 10), text_color='White', background_color='#4267B2',
                justification="Left", pad=(5, 5), auto_size_text=False)]

    def preference_view(self):
        layout1 = [
            [sg.Txt("Station Name", size=15), sg.InputText(default_text=self.default_settings.get('-station-', ''), size=30,
                                                           key="-Station_Name-"), sg.Stretch(),
             sg.B("Validate", size=10)],
            [sg.Txt("Station Type", size=15), sg.DropDown(values=["a", "b"], size=30, readonly=True), sg.Stretch(),
             sg.B("Set", size=10)],
            [sg.HorizontalSeparator()],
            [sg.Txt("Input Folder", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FolderBrowse(size=(10,1), tooltip="abcasdfasdf", target=(sg.ThisRow, -2))],
            [sg.Txt("Output Folder", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FolderBrowse(size=(10,1), target=(sg.ThisRow, -2))],
            [sg.HorizontalSeparator()],
            [sg.Txt("Golden Database", size=15), sg.InputText(size=30, readonly=True), sg.Stretch(),
             sg.FileBrowse(size=(10,1), target=(sg.ThisRow, -2))],
            [sg.Txt("Auto Sync", size=15), sg.Rad("ON", group_id="auto_sync"), sg.Rad("OFF", group_id="auto_sync")],
            [sg.Btn("Save Preference", size=15),sg.Btn("New Window",key="-New_Window-")]
        ]

        window = sg.Window('Preference', layout1, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True)
        return window

    def rel_lab_station_view(self):
        layout1 = [
            [self.__facebook__()],
            [sg.Txt("WIP"),sg.In()],
            []
        ]

        window = sg.Window('Popup', layout1, keep_on_top=False, grab_anywhere=True, no_titlebar=False,
                           finalize=True)
        return window

    @staticmethod
    def welcome_page():
        layout1 = [
            [sg.Sizer(200,10)],
            [sg.Txt("Rel Logger", size=(20,1), font=("Helvetica", 50), text_color='White', background_color='#4267B2',justification="center",pad=(5,40),auto_size_text=False)],
            [sg.Txt("Version 0.1 ", text_color='White', background_color='#4267B2',justification="left", auto_size_text=False)],
            [sg.Txt("from Jimmy Z @facebook. All Right Reserved",text_color='White', background_color='#4267B2',justification="left", auto_size_text=False)]
            ]
        window = sg.Window('Welcome Page', layout1, keep_on_top=False, grab_anywhere=True, no_titlebar=True,
                           finalize=True, auto_close=True, auto_close_duration=5, background_color='#4267B2')
        return window
