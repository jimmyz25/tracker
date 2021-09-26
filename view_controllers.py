# this is a collection of view controllers. each view controller works on a view
import timeit

# import PySimpleGUI as sg
# TODO row security is buggy, if a row is from a station, even
#  it's blocking updating rel_log, it's not preventing it updating Config_SN_T


import PySimpleGUI

from rel_tracker_view import *
from data_model import *


class rel_tracker_app:
    sg.user_settings_filename(path='.')
    settings = sg.user_settings()
    address = settings.get("-Local_Database-")
    print (settings)
    station = settings.get("-Station_Name-")
    view_list = []
    sg.theme("LightGrey1")
    sg.SetOptions(font='Arial 12', element_padding=(2, 2), element_size=(40, 1),
                  auto_size_buttons=True, input_elements_background_color="#f7f7f7")
    dbmodel = DBsqlite(RMD, station=station)

    def __init__(self):
        pass

    # @property
    # def station(self):
    #     return self._station

    @staticmethod
    def apply_user_settings(window: sg.Window):

        for key in rel_tracker_app.settings.keys():
            if isinstance(key, str) and key in window.key_dict.keys():
                if isinstance(window[key], sg.PySimpleGUI.Input) or isinstance(window[key], sg.PySimpleGUI.Combo):
                    window[key].update(value=rel_tracker_app.settings.get(key))
        rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
        rel_tracker_app.dbmodel.station = rel_tracker_app.station
        if "-station_name-" in window.key_dict.keys():
            window["-station_name-"].update(value=rel_tracker_app.station)
        rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
        print("USER SETTINGS APPLIED")

    @staticmethod
    def save_user_settings(window: sg.Window):
        for key in window.key_dict.keys():
            if isinstance(key, str) and isinstance(window[key], sg.PySimpleGUI.Input) \
                    or isinstance(window[key], sg.PySimpleGUI.Combo):
                rel_tracker_app.settings[key] = window[key].get()
        sg.user_settings_save()
        # print()
        print("user setting saved")

    @staticmethod
    def reset_window_inputs(window: sg.Window):
        # clear all input in window
        for key in window.key_dict.keys():
            if isinstance(window[key], sg.PySimpleGUI.Input) or \
                    isinstance(window[key], sg.PySimpleGUI.Combo) or \
                    isinstance(window[key], PySimpleGUI.PySimpleGUI.Multiline):
                window[key].update(value="")
        # clear filterset
        rel_tracker_app.dbmodel.filter_set.clear()
        # save settings to jason file
        rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
        rel_tracker_app.dbmodel.station = rel_tracker_app.station
        print("window reset")


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
        rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
        if self.window["-station-type-"].get() == "RelLog Station":
            rel_tracker_app.view_list.append(rel_log_vc())
        elif self.window["-station-type-"].get() == "FailureMode Logging Station":
            rel_tracker_app.view_list.append(fa_log_vc())
        self.window.close()


class rel_log_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.rel_lab_station_view()
        rel_tracker_app.reset_window_inputs(self.window)
        self.window['-table_select-'].update(values=self.table_data)
        self.complete_quit = True


    @property
    def table_data(self):
        if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
            # if in update mode, do not refresh table, update(values = None) means no update
            return None
        else:
            if rel_tracker_app.dbmodel.display_setting.get("show_latest"):
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
            elif event == "Add":
                print("insert new sn to database")
                rel_tracker_app.dbmodel.filter_set.update(
                    {
                        "station": rel_tracker_app.settings.get("-Station_Name-")
                    }
                )
                rel_tracker_app.dbmodel.insert_new_to_rel_log_table()
                self.window['-table_select-'].update(values=self.table_data)
                self.window["-New-SN_Input-"].update(value="")
                rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
            elif event == "CheckIn":
                rel_tracker_app.dbmodel.filter_set.update(
                    {
                        "station": rel_tracker_app.settings.get("-Station_Name-")
                    }
                )
                stress_popup = stress_select_vc(self.window)
                stress_popup.show()
                if rel_tracker_app.dbmodel.ready_to_checkin:
                    rel_tracker_app.dbmodel.checkin_to_new_checkpoint_rellog_table()
                    rel_tracker_app.reset_window_inputs(self.window)
                    self.window['-table_select-'].update(values=self.table_data)
                else:
                    print("not able to checkin")
            elif event == "Checkout":
                rel_tracker_app.dbmodel.checkout_current_checkpoint_rellog_table()
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "Update":
                rel_tracker_app.dbmodel.update_current_row_rellog_table()
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": False})

                self.window['-table_select-'].update(values=self.table_data)

            elif event.endswith("_Input-") or event.endswith("_count-"):
                if event.startswith("-New-"):
                    # check if exists or any duplicate in the list,clean up and return a string, on backend,
                    # filter set is updated
                    serial_number_list = rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
                    self.window["-New-SN_Input-"].update(
                        value=serial_number_list + "\n")
                    rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-New-WIP_Input-"].get()})
                    self.window["-WIP_Input-"].update(self.window["-New-WIP_Input-"].get())
                else:
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number": self.window["-SN_Input-"].get()})
                    rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-WIP_Input-"].get()})
                    self.window["-New-WIP_Input-"].update(self.window["-WIP_Input-"].get())
                self.window['-table_select-'].update(values=self.table_data)
            elif event.endswith("-ConfigPop-"):
                config_popup = config_select_vc(self.window)
                config_popup.show()
                self.window["-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window["-New-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window['-table_select-'].update(values=self.table_data)
            elif event.endswith("-CkpPop-"):
                stress_popup = stress_select_vc(self.window)
                stress_popup.show()
                self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window["-New-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "Reset":
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-table_select-":
                count = len(values.get('-table_select-'))
                if count == 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": None})
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": None})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": None})
                else:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    # selected = self.window['-table_select-'].get()[values.get('-table_select-')]
                    selected = [self.window['-table_select-'].get()[index] for index in values.get('-table_select-')]
                    selected_sn_list = [row[3] for row in selected]
                    selected_pk_list = [row[0] for row in selected]
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": selected_pk_list})
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": selected_sn_list})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    print(selected_sn_list, "in selection", "Note: ",str(selected[0][-1]))
                    if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
                        sn = SnModel(selected[0][3], database=rel_tracker_app.dbmodel)
                        rel_tracker_app.dbmodel.filter_set.update({
                            "program": sn.config.program,
                            "build": sn.config.build,
                            "config": sn.config.config_name,
                            "wip": sn.wip,
                            "stress": selected[0][4],
                            "checkpoint": selected[0][5],
                            "serial_number": sn.serial_number
                        })
                        self.window["-SN_Input-"].update(str(sn.serial_number))
                        self.window["-Config_Input-"].update(str(sn.config))
                        self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                        self.window["-WIP_Input-"].update(str(sn.wip))
            elif event == "Enter Update Mode":
                self.window['Existing Units'].select()
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": True})
                print("currently in UPDATE MODE, operating on previous record, proceed with CARE, filters stop working")
            elif event == "Exit Update Mode":
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": False})
            elif event == "-show_latest0-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": False})
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-show_latest1-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": True})
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-show_current1-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": rel_tracker_app.dbmodel.station})
                self.window['-table_select-'].update(values=self.table_data)
            elif event == "-show_current0-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": None})
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
            if "_Input-" in event or event == '-table_select-' or event.endswith("_count-") or \
                    event == "Enter Update Mode":
                if rel_tracker_app.dbmodel.ready_to_add and self.window["-Tab_Selection-"].get() == "Register New Unit":
                    self.window["Add"].update(disabled=False)
                else:
                    self.window["Add"].update(disabled=True)

                if rel_tracker_app.dbmodel.ready_to_batch_update and self.window["-Tab_Selection-"].get() == "Register New Unit":
                    self.window["Batch Update"].update(disabled=False)
                else:
                    self.window["Batch Update"].update(disabled=True)

                if rel_tracker_app.dbmodel.ready_to_update and len(values.get('-table_select-')) == 1:
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
        rel_tracker_app.reset_window_inputs(self.window)
        self.window['-table_select-'].update(values=self.rel_table_data)
        self.window["-fa_table_select-"].update(values=self.fa_table_data)
        self.complete_quit = True

    @property
    def rel_table_data(self):
        if rel_tracker_app.dbmodel.display_setting.get("show_latest"):
            datasource = rel_tracker_app.dbmodel.latest_sn_history
        else:
            datasource = rel_tracker_app.dbmodel.rel_log_table_view_data
        data = [[row.get("PK"), row.get("SerialNumber"), row.get("RelStress"),
                 row.get("RelCheckpoint")] for row in
                datasource]
        return data

    @property
    def fa_table_data(self):
        datasource = rel_tracker_app.dbmodel.fa_log_table_view_data
        data = [[row.get("PK"), row.get("FailureGroup"), row.get("FailureMode"),
                 row.get("SerialNumber"), row.get("RelStress"),
                 row.get("RelCheckpoint"), row.get("StartTime"), row.get("FA_Details")] for row in
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
            elif event == "Report Failure":
                failure_mode_popup = failure_mode_vc(self.window)
                failure_mode_popup.show()
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_mode": None
                })
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
            elif event == "Configure Failure Modes":
                failure_mode_config_popup = failure_mode_config_vc(self.window)
                failure_mode_config_popup.show()
            elif event.endswith("_Input-"):
                rel_tracker_app.dbmodel.filter_set.update({"serial_number": self.window["-SN_Input-"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-WIP_Input-"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"failure_mode": values.get("-Failure_Mode_Input-")})

                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
            elif event.endswith("-ConfigPop-"):
                config_popup = config_select_vc(self.window)
                config_popup.show()
                self.window["-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
            elif event.endswith("-CkpPop-"):
                stress_popup = stress_select_vc(self.window)
                stress_popup.show()
                self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
            elif event == "Reset Filter":
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
            elif event == "-table_select-":
                # selecting srialnumber table will set filters to selection row state
                count = len(values.get('-table_select-'))
                if count > 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    selected = self.window['-table_select-'].get()[values.get('-table_select-')[0]]  # first one
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    sn = SnModel(selected[1], database=rel_tracker_app.dbmodel)
                    rel_tracker_app.dbmodel.filter_set.update({
                        "program": sn.config.program,
                        "build": sn.config.build,
                        "config": sn.config.config_name,
                        "wip": sn.wip,
                        "stress": selected[2],
                        "checkpoint": selected[3],
                        "serial_number": sn.serial_number
                    })
                    self.window["-fa_table_select-"].update(values=self.fa_table_data)

            elif event == "-fa_table_select-":
                count = len(values.get('-fa_table_select-'))
                if count > 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-fa_table_select-')})
                    selected = self.window['-fa_table_select-'].get()[values.get('-fa_table_select-')[0]]  # first one
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-fa_table_select-')})
                    sn = SnModel(selected[3], database=rel_tracker_app.dbmodel)
                    rel_tracker_app.dbmodel.filter_set.update({
                        "program": sn.config.program,
                        "build": sn.config.build,
                        "config": sn.config.config_name,
                        "wip": sn.wip,
                        "stress": selected[4],
                        "checkpoint": selected[5],
                        "serial_number": sn.serial_number
                    })
                    self.window["-table_select-"].update(values=self.rel_table_data)

            elif event == "-show_latest0-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": False})
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_latest1-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": True})
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_current1-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": rel_tracker_app.dbmodel.station})
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_current0-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": None})
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.window['-table_select-'].update(values=self.rel_table_data)
            if len(values.get("-fa_table_select-")) > 0 or len(values.get("-table_select-")) > 0:
                # self.window["Update Failure"].update(disabled=False)
                self.window["Report Failure"].update(disabled=False)
            else:
                # self.window["Update Failure"].update(disabled=True)
                self.window["Report Failure"].update(disabled=True)

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
            elif event in ("Program", "Build"):
                rel_tracker_app.dbmodel.filter_set.update({"program": self.window["Program"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"build": self.window["Build"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"config": None})
                self.window["Config"].update(value="",
                                             values=list(rel_tracker_app.dbmodel.config_list_to_select))
            elif event == "Config":
                rel_tracker_app.dbmodel.filter_set.update({"config": self.window["Config"].get()})

            elif event == "-Save-":
                rel_tracker_app.dbmodel.filter_set.update({"program": self.window["Program"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"build": self.window["Build"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"config": self.window["Config"].get()})
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

    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_stress_select()
        self.master = master
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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


class failure_mode_vc:

    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        rel_tracker_app.dbmodel.filter_set.update({
            "station": rel_tracker_app.settings.get('-Station_Name-')
        })
        self.window = view.popup_fm_select()
        self.window["-SN_Input-"].update(str(rel_tracker_app.dbmodel.filter_set.get("serial_number")))
        self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
        self.highlighted_selection = None

        self.window["-highlighted_failures-"].update(values=self.existing_failure_mode_table_data)
        self.window["-failure_mode_set-"].update(value="Default",
                                                 values=list(rel_tracker_app.dbmodel.failure_mode_group_list))
        rel_tracker_app.dbmodel.filter_set.update({"failure_group": self.window["-failure_mode_set-"].get()})
        self.window["-failure_to_select-"].update(values=list(rel_tracker_app.dbmodel.failure_mode_list_to_add_to_sn))
        self.master = master
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())

    @property
    def existing_failure_mode_table_data(self):
        datasource = rel_tracker_app.dbmodel.cache_failure_mode_of_sn_table
        data = [[row.get("PK"), row.get("FailureGroup"), row.get("FailureMode"),
                 row.get("FA_Details")] for row in
                datasource]
        return data

    def show(self):

        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "-failure_mode_set-":
                rel_tracker_app.dbmodel.filter_set.update({"failure_group": self.window["-failure_mode_set-"].get()})
                self.window["-failure_to_select-"].update(values=rel_tracker_app.dbmodel.failure_mode_list_to_add_to_sn)
            elif event == "-failure_to_select- ":
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_mode": values.get('-failure_to_select-')
                })

            elif event == "-Add-":
                sn = self.window["-SN_Input-"].get()
                rel_tracker_app.dbmodel.filter_set.update({"failure_mode": values.get('-failure_to_select-')})
                rel_tracker_app.dbmodel.insert_to_failure_log_table()
                print(f"{values.get('-failure_to_select-')} added for {sn}")
                self.window["-failure_to_select-"].update(values=rel_tracker_app.dbmodel.failure_mode_list_to_add_to_sn)
                self.window["-highlighted_failures-"].update(values=self.existing_failure_mode_table_data)
            elif event == "-Remove-":
                rel_tracker_app.dbmodel.delete_from_failure_log_table()
                self.window["-failure_to_select-"].update(values=rel_tracker_app.dbmodel.failure_mode_list_to_add_to_sn)
                self.window["-highlighted_failures-"].update(values=self.existing_failure_mode_table_data)
                print("remove something")
            elif event == "-highlighted_failures-":
                rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-highlighted_failures-')})
                selected = [self.window['-highlighted_failures-']
                                .get()[index] for index in values.get('-highlighted_failures-')]

                selected_pk = [row[0] for row in selected]
                rel_tracker_app.dbmodel.filter_set.update({"selected_pks": selected_pk})
                if len(selected) > 0:
                    if selected[0][3] is None:
                        self.window["-fa-detail-"].update(value="")
                    else:
                        self.window["-fa-detail-"].update(value=selected[0][3])
            elif event == "Add details":
                if self.window["-fa-detail-"].get() is None:
                    detail = ""
                else:
                    detail = self.window["-fa-detail-"].get()
                log = {
                    "FA_Details": detail
                }
                rel_tracker_app.dbmodel.update_failure_log_table(**log)
                # self.window["-highlighted_failures-"].update(values=None)
                # self.highlighted_selection = values.get("-highlighted_failures-")
                self.window["-highlighted_failures-"].update(values=self.existing_failure_mode_table_data)
            if len(values.get("-highlighted_failures-")) > 0:
                self.window["Add details"].update(disabled=False)
                self.window["-Remove-"].update(disabled=False)
            else:
                self.window["Add details"].update(disabled=True)
                self.window["-Remove-"].update(disabled=True)
            if len(values.get("-failure_to_select-")) > 0:
                self.window["-Add-"].update(disabled=False)
            else:
                self.window["-Add-"].update(disabled=True)

        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()


class failure_mode_config_vc:

    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_fm_config()
        self.master = master
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
        self.window["-failure_mode_set-"].update(value="Default",
                                                 values=list(rel_tracker_app.dbmodel.failure_mode_group_list))
        rel_tracker_app.dbmodel.filter_set.update({
            "failure_group": "Default"
        })
        self.window["-failure_mode_list-"].update(values=rel_tracker_app.dbmodel.failure_mode_list)

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Create New Failure Mode":
                failure_mode = sg.popup_get_text("Please Provide Failure Mode Name")
                rel_tracker_app.dbmodel.insert_to_failure_mode_table(failure_mode)
                self.window["-failure_mode_set-"].update(value="Default",
                                                         values=list(rel_tracker_app.dbmodel.failure_mode_group_list))
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_group": "Default"
                })
                self.window["-failure_mode_list-"].update(values=rel_tracker_app.dbmodel.failure_mode_list)
            elif event == "-failure_mode_set-":
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_group": values.get("-failure_mode_set-")
                })
                self.window["-failure_mode_list-"].update(values=list(rel_tracker_app.dbmodel.failure_mode_list))
            elif event == "-failure_mode_list-":
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_mode": values.get("-failure_mode_list-")
                })
            elif event == "Group Failure Modes":
                failure_group = sg.popup_get_text("Please Provide Group Name")
                rel_tracker_app.dbmodel.update_failure_mode_table(group_name=failure_group)
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_group": failure_group
                })
                self.window["-failure_mode_set-"].update(value=failure_group,
                                                         values=list(rel_tracker_app.dbmodel.failure_mode_group_list))
                self.window["-failure_mode_list-"].update(values=list(rel_tracker_app.dbmodel.failure_mode_list))
            elif event == "Archive Failure Mode":
                user_agreement = sg.popup_ok_cancel("Delete failure mode will NOT remove previous input to FA Log")
                if user_agreement == "OK":
                    rel_tracker_app.dbmodel.delete_from_failure_mode_table()
                self.window["-failure_mode_list-"].update(values=list(rel_tracker_app.dbmodel.failure_mode_list))
            if len(values.get("-failure_mode_list-")) > 0:
                self.window["Group Failure Modes"].update(disabled=False)
                self.window["Archive Failure Mode"].update(disabled=False)
            else:
                self.window["Group Failure Modes"].update(disabled=True)
                self.window["Archive Failure Mode"].update(disabled=True)
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()
