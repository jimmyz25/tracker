# this is a collection of view controllers. each view controller works on a view

import PySimpleGUI as sg
from rel_tracker_view import *


class rel_tracker_app:

    sg.user_settings_filename(path='.')
    settings = sg.user_settings()
    view_list = []
    sg.theme("LightGrey1")
    sg.SetOptions(font='Arial 12', element_padding=(2, 2), element_size=(40, 1),
                  auto_size_buttons=True)

    def __init__(self):
        self.settings = None
        self.initialize()

    def initialize(self):
        pass


class welcome_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.welcome_page()
        self.show()

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break


# class popup_view1:
#     def __init__(self, app:rel_tracker_app):
#         view = rel_tracker_view(app.settings)
#         self.window = view.rel_lab_station_view()
#
#     def show(self):
#         while True:  # the event loop
#             event, values = self.window.read()
#             if event == sg.WIN_CLOSED:
#                 break
#             elif event == "Save Preference":
#                 self.window['-station-'] = values['-Station_Name-']
#         self.close_window()
#
#     def close_window(self):
#         sg.user_settings_save()
#         self.window.close()


class template_view(rel_tracker_app):
    def __init__(self):
        """
        :param app: rel_tracker_app
        view: view class, do not write
        window: a vc to display and control a view from view class
        """
        self.__view__ = rel_tracker_view(rel_tracker_app.settings)
        self.window = self.__view__.rel_lab_station_view()
        self.window['-Home-'].bind('<Button-1>',"")
        rel_tracker_app.view_list.append(self.window)
        self.show()

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Save Preference":
                rel_tracker_app.settings['-station-'] = values['-Station_Name-']
            elif event == "-Home-":
                preference = preference_vc()
                self.close_window()
                preference.show()
            elif event == "-table_select-":
                print (event,values)
            print(event,values)
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()
        rel_tracker_app.view_list.pop()
        if len(rel_tracker_app.view_list)>0:
            window = rel_tracker_app.view_list.pop()
            window.show()


class preference_vc(template_view):
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.preference_view()

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Save Preference":
                rel_tracker_app.settings['-station-'] = values['-Station_Name-']
        self.close_window()
    #
    # def close_window(self):
    #     sg.user_settings_save()
    #     self.window.close()