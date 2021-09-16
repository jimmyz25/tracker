# this is a collection of view controllers. each view controller works on a view
import timeit

import PySimpleGUI as sg
from rel_tracker_view import *
from data_model import *


class rel_tracker_app:
    sg.user_settings_filename(path='.')
    settings = sg.user_settings()

    view_list = []
    sg.theme("LightGrey1")
    sg.SetOptions(font='Arial 12', element_padding=(2, 2), element_size=(40, 1),
                  auto_size_buttons=True, input_elements_background_color="#f7f7f7")
    dbmodel = DBsqlite(RMD)

    def __init__(self):
        pass

    @staticmethod
    def apply_user_settings(window: sg.Window):
        for key in rel_tracker_app.settings.keys():
            if isinstance(key, str) and key in window.key_dict.keys():
                if isinstance(window[key], sg.PySimpleGUI.Input):
                    window[key].update(value=rel_tracker_app.settings.get(key))
        rel_tracker_app.dbmodel.filter_set = rel_tracker_app.settings["filter_set"]

    @staticmethod
    def save_user_settings(window: sg.Window):
        for key in window.key_dict.keys():
            if isinstance(key, str) and isinstance(window[key], sg.PySimpleGUI.Input):
                rel_tracker_app.settings[key] = window[key].get()
        rel_tracker_app.settings["filter_set"] = rel_tracker_app.dbmodel.filter_set
        sg.user_settings_save()

    @classmethod
    def reset_window_inputs(cls, window: sg.Window):
        # clear all input in window
        for key in window.key_dict.keys():
            if isinstance(key, str) and isinstance(window[key], sg.PySimpleGUI.Input):
                window[key].update(value="")
        # clear filterset
        cls.dbmodel.filter_set.clear()
        # save settings to jason file
        cls.save_user_settings(window)


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


class template_view:
    def __init__(self):
        """
        view: view class, do not write
        window: a vc to display and control a view from view class
        """
        self.__view__ = rel_tracker_view(rel_tracker_app.settings)
        self.window = self.__view__.rel_lab_station_view()
        self.window['-Home-'].bind('<Button-1>', "")
        rel_tracker_app.view_list.append(self.window)
        # self.show()

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Save Preference":
                rel_tracker_app.settings['-station-'] = values['-Station_Name-']
            elif event == "-Home-":
                preference = preference_vc()
                preference.show()

            elif event == "-table_select-":
                print(event, values)
            print(event, values)
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()
        rel_tracker_app.view_list.pop()
        if len(rel_tracker_app.view_list) > 0:
            window = rel_tracker_app.view_list.pop()
            window.show()


class preference_vc:

    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)

        self.window = view.preference_view()
        rel_tracker_app.apply_user_settings(self.window)
        self.window["-station-type"].update(values=["a", "b", "c"])

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Save Preference":
                rel_tracker_app.save_user_settings(self.window)
            print(event, values)
        self.close_window()

    def close_window(self):
        # selection = self.window["-station-type"].get()

        self.window.close()
        # if selection == "a":
        #     print("will go to rel_lab_station")
        #     view = rel_tracker_view.rel_lab_station_view()
        #     view.show()


class rel_log_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.rel_lab_station_view()
        rel_tracker_app.view_list.append(self)
        rel_tracker_app.apply_user_settings(self.window)
        self.window['-table_select-'].update(values=self.table_data)

    # def __update_view__(self, values):
    #     if values.get("-table_select-") is not None:
    #         # add, checkin, checkout,update,delete is avialbe
    #         pass

    @property
    def table_data(self):
        if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
            return None
        else:
            datasource = rel_tracker_app.dbmodel.rel_log_table_view_data
            data = [[row.get("PK"), row.get("Config"), row.get("WIP"), row.get("SerialNumber"), row.get("RelStress"),
                     row.get("RelCheckpoint"), row.get("StartTime"), row.get("EndTime"), row.get("Note")] for row in
                    datasource]
            return data

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Save Preference":
                rel_tracker_app.settings['-station-'] = values['-Station_Name-']
            elif event == "-Home-":
                preference = preference_vc()
                preference.show()
            elif event.endswith("_Input-") or event.endswith("_count-"):
                if event.startswith("-New-"):
                    serial_number_list = rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
                    self.window["-New-SN_Input-"].update(
                        value=serial_number_list + "\n")
                    rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-New-WIP_Input-"].get()})
                    # if rel_tracker_app.dbmodel.ready_to_add:
                    #     self.window["Add"].update(disabled=False)
                    # else:
                    #     self.window["Add"].update(disabled=True)
                else:
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number": self.window["-SN_Input-"].get()})
                    rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-WIP_Input-"].get()})
                    if rel_tracker_app.dbmodel.sn_exist(self.window["-SN_Input-"].get()):
                        sn = SnModel(self.window["-SN_Input-"].get(), database=rel_tracker_app.dbmodel)
                        self.window["-SN_Input-"].update(str(sn.serial_number))
                        self.window["-Config_Input-"].update(str(sn.config))
                        self.window["-Ckp_Input-"].update(str(sn.stress))
                        self.window["-WIP_Input-"].update(str(sn.wip))
                self.window['-table_select-'].update(values=self.table_data)
            elif event.endswith("-ConfigPop-"):
                config_popup = config_select_vc(self.window)
                config_popup.show()
                self.window["-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window["-New-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window['-table_select-'].update(values=self.table_data)
            elif event.endswith("-CkpPop-"):
                stress_popup = stress_select_vc()
                stress_popup.show()
                self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window["-New-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "Reset":
                # self.window["-SN_Input-"].update(value="")
                # self.window["-Config_Input-"].update(value="")
                # self.window["-Ckp_Input-"].update(value="")
                # self.window["-WIP_Input-"].update(value="")
                # self.window["-New-SN_Input-"].update(value="")
                # self.window["-New-Config_Input-"].update(value="")
                # self.window["-New-Ckp_Input-"].update(value="")
                # self.window["-New-WIP_Input-"].update(value="")
                # rel_tracker_app.dbmodel.filter_set.clear()
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-table_select-":
                if len(values.get('-table_select-')) > 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pk": values.get('-table_select-')})
            elif event == "update":
                self.window['Existing Units'].select()
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": True})
                selected = self.window['-table_select-'].get()[values.get('-table_select-')[0]]  # first one
                rel_tracker_app.dbmodel.filter_set.update({"selected_pk": values.get('-table_select-')})
                sn = SnModel(selected[3], database=rel_tracker_app.dbmodel)
                self.window["-SN_Input-"].update(str(sn.serial_number))
                self.window["-Config_Input-"].update(str(sn.config))
                self.window["-Ckp_Input-"].update(str(sn.stress))
                self.window["-WIP_Input-"].update(str(sn.wip))
                rel_tracker_app.dbmodel.filter_set.update({
                    "program": sn.config.program,
                    "build": sn.config.build,
                    "config": sn.config.config_name,
                    "wip": sn.wip,
                    "stress": sn.stress.rel_stress,
                    "checkpoint": sn.stress.rel_checkpoint,
                    "serial_number": sn.serial_number
                })
            print(rel_tracker_app.dbmodel.filter_set)
            print(event, values)
            # after each input, check app status and enable or disable buttons
            if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
                self.window['Register New Unit'].update(disabled=True)
                for key in self.window.AllKeysDict.keys():
                    if isinstance(key, str):
                        if key.endswith("Input-") or key.endswith("-Note-"):
                            self.window[key].update(background_color="#ecdab9")
            else:
                self.window['Register New Unit'].update(disabled=False)
                for key in self.window.AllKeysDict.keys():
                    if isinstance(key, str):
                        if key.endswith("Input-") or key.endswith("-Note-"):
                            self.window[key].update(background_color="#f7f7f7")
            if "_Input-" in event or event == '-table_select-' or event.endswith("_count-") or event=="update":
                if rel_tracker_app.dbmodel.ready_to_add and self.window["-Tab_Selection-"].get() == "Register New Unit":
                    self.window["Add"].update(disabled=False)
                else:
                    self.window["Add"].update(disabled=True)
                if rel_tracker_app.dbmodel.ready_to_update:
                    self.window["Update"].update(disabled=False)
                else:
                    self.window["Update"].update(disabled=True)
                if rel_tracker_app.dbmodel.ready_to_checkin:
                    self.window["CheckIn"].update(disabled=False)
                else:
                    self.window["CheckIn"].update(disabled=True)
                if rel_tracker_app.dbmodel.ready_to_checkout and len(values.get('-table_select-')) > 0:
                    self.window["Checkout"].update(disabled=False)
                else:
                    self.window["Checkout"].update(disabled=True)
                if rel_tracker_app.dbmodel.filter_set.get("selected_pk"):
                    self.window["Delete"].update(disabled=False)
                else:
                    self.window["Delete"].update(disabled=True)
                if rel_tracker_app.dbmodel.filter_set.get("serial_number_list") is not None:
                    total_sn_to_register = len(rel_tracker_app.dbmodel.filter_set.get("serial_number_list"))
                    self.window["-Multi_SN-"].update(value=f'SerialNumber ({total_sn_to_register})')
        self.close_window()

    def close_window(self):
        self.window.close()
        print("window closed")
        rel_tracker_app.save_user_settings(self.window)
        sys.exit()


class config_select_vc:
    def __init__(self, master: sg.Window):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_config_select()
        self.master = master
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
        rel_tracker_app.view_list.append(self)
        # program_list = rel_tracker_app.dbmodel.program_list
        self.window["Program"].update(value=rel_tracker_app.dbmodel.filter_set.get("program"),
                                      values=list(rel_tracker_app.dbmodel.program_list))
        self.window["Build"].update(value=rel_tracker_app.dbmodel.filter_set.get("build"),
                                    values=list(rel_tracker_app.dbmodel.build_list))
        self.window["Config"].update(value=rel_tracker_app.dbmodel.filter_set.get("config"),
                                     values=list(rel_tracker_app.dbmodel.config_list_to_select))

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event.endswith("KeyPress"):
                temp_program_input = self.window["Program"].get()
                self.window["Program"].update(value=temp_program_input,
                                              values=list(
                                                  filter(lambda x: x.startswith(self.window["Program"].get()),
                                                         rel_tracker_app.dbmodel.program_list)))
            elif event in ("Program", "Build", "Config"):
                print("something is selected")
                if event == "Config":
                    temp_config_selection = self.window["Config"].get()
                else:
                    temp_config_selection = None
                rel_tracker_app.dbmodel.filter_set.update({"program": self.window["Program"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"build": self.window["Build"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"config": self.window["Config"].get()})
                self.window["Config"].update(value=temp_config_selection,
                                             values=list(rel_tracker_app.dbmodel.config_list_to_select))
            elif event == "-Save-":
                break
            elif event == "-Clear-":
                rel_tracker_app.dbmodel.filter_set.update({"program": None})
                rel_tracker_app.dbmodel.filter_set.update({"build": None})
                rel_tracker_app.dbmodel.filter_set.update({"config": None})
                self.window["Program"].update(values=list(rel_tracker_app.dbmodel.program_list))
                self.window["Build"].update(values=list(rel_tracker_app.dbmodel.build_list))
                self.window["Config"].update(values=list(rel_tracker_app.dbmodel.config_list_to_select))
        self.close_window()

    def close_window(self):
        self.window.close()


class stress_select_vc:

    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_stress_select()
        self.window.TKroot.grab_set()
        rel_tracker_app.view_list.append(self)
        # program_list = rel_tracker_app.dbmodel.program_list
        self.window["RelStress"].update(value=rel_tracker_app.dbmodel.filter_set.get("stress"),
                                        values=list(rel_tracker_app.dbmodel.stress_list))
        self.window["RelCheckpoint"].update(value=rel_tracker_app.dbmodel.filter_set.get("checkpoint"),
                                            values=list(rel_tracker_app.dbmodel.ckp_list_to_select))

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event.endswith("KeyPress"):
                temp_program_input = self.window["RelStress"].get()
                self.window["RelStress"].update(value=temp_program_input,
                                                values=list(
                                                    filter(lambda x: x.startswith(self.window["RelStress"].get()),
                                                           rel_tracker_app.dbmodel.program_list)))
            elif event in ("RelStress", "RelCheckpoint"):
                print("something is selected")
                if event == "RelCheckpoint":
                    temp_ckp_selection = self.window["RelCheckpoint"].get()
                else:
                    temp_ckp_selection = None
                rel_tracker_app.dbmodel.filter_set.update({"stress": self.window["RelStress"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"checkpoint": self.window["RelCheckpoint"].get()})
                self.window["RelCheckpoint"].update(value=temp_ckp_selection,
                                                    values=list(rel_tracker_app.dbmodel.ckp_list_to_select))
            elif event == "-Save-":
                self.close_window()
            elif event == "-Clear-":
                rel_tracker_app.dbmodel.filter_set.update({"stress": None})
                rel_tracker_app.dbmodel.filter_set.update({"checkpoint": None})
                self.window["RelStress"].update(value=None, values=list(rel_tracker_app.dbmodel.stress_list))
                self.window["RelCheckpoint"].update(values=list(rel_tracker_app.dbmodel.ckp_list_to_select))
            print(event, values)
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()
