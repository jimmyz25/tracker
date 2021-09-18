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
                if isinstance(window[key], sg.PySimpleGUI.Input) or isinstance(window[key], sg.PySimpleGUI.Combo):
                    window[key].update(value=rel_tracker_app.settings.get(key))
        station_name = str(rel_tracker_app.settings.get('-Station_Name-'))
        if "-station_name-" in window.key_dict.keys():
            window["-station_name-"].update(value=station_name)
        rel_tracker_app.dbmodel.filter_set = rel_tracker_app.settings["filter_set"]
        print("USER SETTINGS APPLIED")

    @staticmethod
    def save_user_settings(window: sg.Window):
        for key in window.key_dict.keys():
            if isinstance(key, str) and isinstance(window[key], sg.PySimpleGUI.Input) \
                    or isinstance(window[key], sg.PySimpleGUI.Combo):
                rel_tracker_app.settings[key] = window[key].get()
        rel_tracker_app.settings["filter_set"] = rel_tracker_app.dbmodel.filter_set
        sg.user_settings_save()
        print("user setting saved")

    @classmethod
    def reset_window_inputs(cls, window: sg.Window):
        # clear all input in window
        for key in window.key_dict.keys():
            if isinstance(window[key], sg.PySimpleGUI.Input) or isinstance(window[key], sg.PySimpleGUI.Combo):
                window[key].update(value="")
        # clear filterset
        cls.dbmodel.filter_set.clear()
        # save settings to jason file
        cls.save_user_settings(window)
        print("window rested")


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
        self.window["-station-type-"].update(values=["RelLog Station", "FailureMode Logging Station", "c"])
        rel_tracker_app.apply_user_settings(self.window)

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == "-WINDOW CLOSE ATTEMPTED-":
                break
            elif event == "Save Preference":
                rel_tracker_app.save_user_settings(self.window)

        self.close_window()

    def close_window(self):

        rel_tracker_app.save_user_settings(self.window)
        if self.window["-station-type-"].get() == "RelLog Station":
            rel_tracker_app.view_list.append(rel_log_vc())
        elif self.window["-station-type-"].get() == "FailureMode Logging Station":
            rel_tracker_app.view_list.append(fa_log_vc())
        self.window.close()


class rel_log_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.rel_lab_station_view()
        rel_tracker_app.apply_user_settings(self.window)
        rel_tracker_app.dbmodel.filter_set.update({"update_mode": False})
        self.window['-table_select-'].update(values=self.table_data)
        self.complete_quit = True

    # def __update_view__(self, values):
    #     if values.get("-table_select-") is not None:
    #         # add, checkin, checkout,update,delete is avialbe
    #         pass

    @property
    def table_data(self):
        if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
            # if in update mode, do not refresh table, update(values = None) means no update
            return None
        else:
            if rel_tracker_app.dbmodel.filter_set.get("show_latest"):
                datasource = rel_tracker_app.dbmodel.latest_sn_history
            else:
                datasource = rel_tracker_app.dbmodel.rel_log_table_view_data
            data = [[row.get("PK"), row.get("Config"), row.get("WIP"), row.get("SerialNumber"), row.get("RelStress"),
                     row.get("RelCheckpoint"), row.get("StartTime"), row.get("EndTime"), row.get("Note")] for row in
                    datasource]
            return data

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if not isinstance(event, str):
                continue
            if event == "-WINDOW CLOSE ATTEMPTED-":
                break
            elif event == "Save Preference":
                rel_tracker_app.settings['-station-'] = values['-Station_Name-']
            elif event == "-Home-":
                self.complete_quit = False
                preference = preference_vc()
                rel_tracker_app.view_list.append(preference)
                break
            elif event.endswith("_Input-") or event.endswith("_count-"):
                if event.startswith("-New-"):
                    serial_number_list = rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
                    self.window["-New-SN_Input-"].update(
                        value=serial_number_list + "\n")
                    rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-New-WIP_Input-"].get()})
                    self.window["-WIP_Input-"].update(self.window["-New-WIP_Input-"].get())
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
                    self.window["-New-WIP_Input-"].update(self.window["-WIP_Input-"].get())
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
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-table_select-":
                count = len(values.get('-table_select-'))
                if count > 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    # selected = self.window['-table_select-'].get()[values.get('-table_select-')]
                    selected = [self.window['-table_select-'].get()[index] for index in values.get('-table_select-')]
                    selected_sn = [row[3] for row in selected]
                    self.window["-note_show-"].update(value=str(selected[0][-1]))
                    print(selected_sn, "in selection")
                if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
                    selected = self.window['-table_select-'].get()[values.get('-table_select-')[0]]  # first one
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
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
            elif event == "update":
                self.window['Existing Units'].select()
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": True})

                print("currently in UPDATE MODE, operating on previous record, proceed with CARE, filters stop working")
            elif event == "-show_latest0-":
                rel_tracker_app.dbmodel.filter_set.update({"show_latest": False})
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-show_latest1-":
                rel_tracker_app.dbmodel.filter_set.update({"show_latest": True})
                self.window['-table_select-'].update(values=self.table_data)
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
            if "_Input-" in event or event == '-table_select-' or event.endswith("_count-") or event == "update":
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
                if rel_tracker_app.dbmodel.filter_set.get("selected_row"):
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
        if self.complete_quit:
            sys.exit()


class fa_log_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.fa_log_view()
        rel_tracker_app.apply_user_settings(self.window)
        self.window['-table_select-'].update(values=self.table_data)
        self.complete_quit = True

    @property
    def table_data(self):
        if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
            # if in update mode, do not refresh table, update(values = None) means no update
            return None
        else:
            if rel_tracker_app.dbmodel.filter_set.get("show_latest"):
                datasource = rel_tracker_app.dbmodel.latest_sn_history
            else:
                datasource = rel_tracker_app.dbmodel.rel_log_table_view_data
            data = [[row.get("PK"), row.get("Config"), row.get("WIP"), row.get("SerialNumber"), row.get("RelStress"),
                     row.get("RelCheckpoint"), row.get("StartTime"), row.get("EndTime"), row.get("Note")] for row in
                    datasource]
            return data

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if not isinstance(event, str):
                continue
            if event == "-WINDOW CLOSE ATTEMPTED-":
                break
            elif event == "-Home-":
                self.complete_quit = False
                preference = preference_vc()
                rel_tracker_app.view_list.append(preference)
                break
            elif event.endswith("_Input-") or event.endswith("_count-"):
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
                self.window['-table_select-'].update(values=self.table_data)
            elif event.endswith("-CkpPop-"):
                stress_popup = stress_select_vc()
                stress_popup.show()
                self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "Reset Filter":
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-table_select-":
                count = len(values.get('-table_select-'))
                if count > 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    # selected = self.window['-table_select-'].get()[values.get('-table_select-')]
                    selected = [self.window['-table_select-'].get()[index] for index in values.get('-table_select-')]
                    selected_sn = [row[3] for row in selected]
                    selected = self.window['-table_select-'].get()[values.get('-table_select-')[0]]  # first one
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
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
                    print(selected_sn, "in selection")
            elif event == "-show_latest0-":
                rel_tracker_app.dbmodel.filter_set.update({"show_latest": False})
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-show_latest1-":
                rel_tracker_app.dbmodel.filter_set.update({"show_latest": True})
                self.window['-table_select-'].update(values=self.table_data)

            # if "_Input-" in event or event == '-table_select-' or event.endswith("_count-") or event == "update":
            #     if rel_tracker_app.dbmodel.ready_to_add and self.window["-Tab_Selection-"].get() == "Register New Unit":
            #         self.window["Add"].update(disabled=False)
            #     else:
            #         self.window["Add"].update(disabled=True)
            #     if rel_tracker_app.dbmodel.ready_to_update:
            #         self.window["Update"].update(disabled=False)
            #     else:
            #         self.window["Update"].update(disabled=True)
            #     if rel_tracker_app.dbmodel.ready_to_checkin:
            #         self.window["CheckIn"].update(disabled=False)
            #     else:
            #         self.window["CheckIn"].update(disabled=True)
            #     if rel_tracker_app.dbmodel.ready_to_checkout and len(values.get('-table_select-')) > 0:
            #         self.window["Checkout"].update(disabled=False)
            #     else:
            #         self.window["Checkout"].update(disabled=True)
            #     if rel_tracker_app.dbmodel.filter_set.get("selected_row"):
            #         self.window["Delete"].update(disabled=False)
            #     else:
            #         self.window["Delete"].update(disabled=True)
            #     if rel_tracker_app.dbmodel.filter_set.get("serial_number_list") is not None:
            #         total_sn_to_register = len(rel_tracker_app.dbmodel.filter_set.get("serial_number_list"))
            #         self.window["-Multi_SN-"].update(value=f'SerialNumber ({total_sn_to_register})')

        self.close_window()

    def close_window(self):
        self.window.close()
        print("window closed")
        rel_tracker_app.save_user_settings(self.window)
        if self.complete_quit:
            sys.exit()


class config_select_vc:
    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_config_select()
        self.master = master
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()
