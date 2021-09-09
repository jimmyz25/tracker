# this is a collection of view controllers. each view controller works on a view

import PySimpleGUI as sg
from rel_tracker_view import *


class rel_tracker_app:
    def __init__(self):
        self.settings = None
        self.initialize()

    def initialize(self):
        sg.theme('Reddit')
        sg.user_settings_filename(path='.')
        self.settings = sg.user_settings()
        # based on context, generate fun first view controller


class loading_page:
    def __init__(self, app:rel_tracker_app):
        view = rel_tracker_view(app.settings)
        self.window = view.welcome_page()
        self.app = app
        self.show()

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break


class view_a:
    def __init__(self, app: rel_tracker_app):
        view = rel_tracker_view(app.settings)
        self.window = view.preference_view()
        self.app = app
        self.show()

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Save Preference":
                self.app.settings['-station-'] = values['-Station_Name-']
            elif event == "-New_Window-":
                popup = popup_view1(self.app)
                self.close_window()
                popup.show()
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()


class popup_view1:
    def __init__(self, app:rel_tracker_app):
        view = rel_tracker_view(app.settings)
        self.window = view.rel_lab_station_view()

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Save Preference":
                self.window['-station-'] = values['-Station_Name-']
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()
#
# while True:  # the event loop
#     event, values = main_window.read()
#     if event == sg.WIN_CLOSED:
#         break
#     elif event == "Save Preference":
#         settings['-station-'] = values['-Station_Name-']
#     elif event == "-New_Window-":
#         popup = app.rel_lab_station_view()
#         while True:  # the event loop
#             event, values = popup.read()
#             if event == sg.WIN_CLOSED:
#                 break
#             elif event == "Save Preference":
#                 settings['-station-'] = values['-Station_Name-'] + "SDFSDF"
# sg.user_settings_save()
# main_window.close()
