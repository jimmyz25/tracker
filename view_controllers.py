# this is a collection of view controllers. each view controller works on a view

from rel_tracker_view import *
from data_model import *
import sys


class rel_tracker_app:
    sg.user_settings_filename(path='.')
    settings = sg.user_settings()
    address = settings.get("-Local_Database-")
    station = settings.get("-Station_Name-")
    view_list = []
    sg.theme("LightGrey1")
    sg.SetOptions(font='Arial 12', element_padding=(2, 2), element_size=(35, 1),
                  auto_size_buttons=False, input_elements_background_color="#f7f7f7", auto_size_text=True)
    while True:
        if DBsqlite.ok2use(address):
            dbmodel = DBsqlite(address, station=station)
            settings.update({"-Local_Database-": address})
            break
        else:
            address = sg.popup_get_file("please select database file")

    def __init__(self):
        pass

    @staticmethod
    def set_address(address):
        rel_tracker_app.dbmodel.__address__ = address

    @staticmethod
    def apply_user_settings(window: sg.Window):
        for key in rel_tracker_app.settings.keys():
            if isinstance(key, str) and key in window.key_dict.keys():
                if isinstance(window[key], sg.PySimpleGUI.Input) or isinstance(window[key], sg.PySimpleGUI.Combo):
                    window[key].update(value=rel_tracker_app.settings.get(key))
        rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
        rel_tracker_app.dbmodel.station = rel_tracker_app.station
        print("USER SETTINGS APPLIED")

    @staticmethod
    def save_user_settings(window: sg.Window):
        for key in window.key_dict.keys():
            if isinstance(key, str) and isinstance(window[key], sg.PySimpleGUI.Input) \
                    or isinstance(window[key], sg.PySimpleGUI.Combo):
                rel_tracker_app.settings[key] = window[key].get()
        sg.user_settings_save()
        rel_tracker_app.set_address(rel_tracker_app.settings.get("-Local_Database-"))

        # print()
        print("user setting saved")

    @staticmethod
    def reset_window_inputs(window: sg.Window):
        # clear all input in window
        for key in window.key_dict.keys():
            if isinstance(window[key], sg.PySimpleGUI.Input) or \
                    isinstance(window[key], sg.PySimpleGUI.Combo) or \
                    isinstance(window[key], sg.PySimpleGUI.Multiline):
                window[key].update(value="")
        # clear filterset
        rel_tracker_app.dbmodel.filter_set.clear()
        # save settings to jason file
        rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
        rel_tracker_app.dbmodel.station = rel_tracker_app.station
        station_name_display = "Station: " + str(rel_tracker_app.station)
        if "-station_name-" in window.key_dict.keys():
            window["-station_name-"].update(value=station_name_display)
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
        self.window["-station-type-"].update(values=["RelLog Station", "FailureMode Logging Station", "Data Tagging"])
        rel_tracker_app.apply_user_settings(self.window)

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == "-WINDOW CLOSE ATTEMPTED-":
                break
            elif event == "Save Preference":
                rel_tracker_app.save_user_settings(self.window)
            elif event == "Stress Setup":
                stress_setup_popup = stress_setup_vc(self.window)
                stress_setup_popup.show()
            elif event == "Configs Setup":
                config_setup_popup = config_setup_vc(self.window)
                config_setup_popup.show()
            elif event == "-Local_Database-":
                address = values.get("-Local_Database-")
                while True:
                    if DBsqlite.ok2use(address):
                        rel_tracker_app.dbmodel = DBsqlite(address,
                                                           station=rel_tracker_app.station)
                        rel_tracker_app.settings.update({"-Local_Database-": address})
                        sg.popup_ok("Great, this database is ok2use. please double \n"
                                    "confirm this is the latest local copy "
                                    "before continuing")
                        break
                    else:
                        address = sg.popup_get_file("please select database file")
        self.close_window()

    def close_window(self):
        rel_tracker_app.save_user_settings(self.window)
        rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
        if self.window["-station-type-"].get() == "RelLog Station":
            rel_tracker_app.view_list.append(rel_log_vc())
            rel_tracker_app.settings.update({"-first_view-": "RelLog Station"})
        elif self.window["-station-type-"].get() == "FailureMode Logging Station":
            rel_tracker_app.view_list.append(fa_log_vc())
            rel_tracker_app.settings.update({"-first_view-": "FailureMode Logging Station"})
        elif self.window["-station-type-"].get() == "Data Tagging":
            rel_tracker_app.view_list.append(data_log_vc())
            rel_tracker_app.settings.update({"-first_view-": "Data Tagging"})
        self.window.close()


class rel_log_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.rel_lab_station_view()
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
            data.sort(key=lambda x: x[3])
            return data

    def show(self):
        rel_tracker_app.reset_window_inputs(self.window)
        self.window['-table_select-'].update(values=self.table_data)
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
            elif event == "Remove for FA":
                wip = "FA"
                if wip is not None:
                    rel_tracker_app.dbmodel.assign_wip_row_rellog_table(wip)
                    rel_tracker_app.dbmodel.filter_set.update({"wip": "FA"})
                    self.window['-table_select-'].update(values=self.table_data)
                    self.window["-New-SN_Input-"].update(value="")
                    # self.window["-WIP_Input-"].update(value="FA")
                    rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
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

            elif event == "Add Dummy SN":
                print("insert new sn to database")
                rel_tracker_app.dbmodel.clean_up_sn_list(rel_tracker_app.dbmodel.generate_random_sn())
                rel_tracker_app.dbmodel.filter_set.update(
                    {
                        "station": rel_tracker_app.settings.get("-Station_Name-"),
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
                    rel_tracker_app.dbmodel.clean_up_sn_list(",".join(selected_sn_list))
                    # rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": selected_sn_list})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    print(selected_sn_list, "in selection", "Note: ", str(selected[0][-1]))
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
            elif event == "Assign WIP":
                wip = sg.popup_get_text("Please Provide New WIP, this will change current checkpoint's WIP")
                if wip is not None:
                    rel_tracker_app.dbmodel.assign_wip_row_rellog_table(wip)
                    self.window['-table_select-'].update(values=self.table_data)
                    self.window["-New-SN_Input-"].update(value="")
                    rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
            elif event == "Delete":
                rel_tracker_app.dbmodel.delete_from_rellog_table()
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
                    event == "Enter Update Mode" or event == "Reset":
                if rel_tracker_app.dbmodel.ready_to_add and self.window["-Tab_Selection-"].get() == "Register New Unit":
                    self.window["Add"].update(disabled=False)
                else:
                    self.window["Add"].update(disabled=True)

                if rel_tracker_app.dbmodel \
                        .ready_to_batch_update and self.window["-Tab_Selection-"].get() == "Register New Unit":
                    self.window["Assign WIP"].update(disabled=False)
                else:
                    self.window["Assign WIP"].update(disabled=True)

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
                    self.window["Remove for FA"].update(disabled=False)
                else:
                    self.window["Delete"].update(disabled=True)
                    self.window["Remove for FA"].update(disabled=True)
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

        self.complete_quit = True

    @property
    def rel_table_data(self):
        if rel_tracker_app.dbmodel.display_setting.get("show_latest"):
            datasource = rel_tracker_app.dbmodel.all_station_latest_sn_history
        else:
            datasource = rel_tracker_app.dbmodel.all_station_rel_log_table_view_data
        data = [[row.get("PK"), row.get("SerialNumber"), row.get("RelStress"),
                 row.get("RelCheckpoint"), row.get("Config"), row.get("EndTime")] for row in
                datasource]
        data.sort(key=lambda x: x[1])
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
        self.window['-table_select-'].update(values=self.rel_table_data)
        self.window["-fa_table_select-"].update(values=self.fa_table_data)
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
                # selecting SerialNumber table will set filters to selection row state
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

            elif event == "-show_latest0-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": False})
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_latest1-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": True})
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_current1-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": rel_tracker_app.dbmodel.station})
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                # self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_current0-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": None})
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                # self.window['-table_select-'].update(values=self.rel_table_data)
            # if len(values.get("-fa_table_select-")) > 0 or len(values.get("-table_select-")) > 0:
            if rel_tracker_app.dbmodel.filter_set.get("selected_row"):
                self.window["Report Failure"].update(disabled=False)
            else:

                self.window["Report Failure"].update(disabled=True)
            print(event, values)
        self.close_window()

    def close_window(self):
        self.window.close()
        print("window closed")
        rel_tracker_app.save_user_settings(self.window)
        if self.complete_quit:
            sys.exit()


class data_log_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.data_log_view()
        rel_tracker_app.reset_window_inputs(self.window)
        self.selected_tagger_pk = None
        self.complete_quit = True

    @property
    def rel_table_data(self):
        if rel_tracker_app.dbmodel.display_setting.get("show_latest"):
            datasource = rel_tracker_app.dbmodel.latest_sn_history
        else:
            datasource = rel_tracker_app.dbmodel.all_station_rel_log_table_view_data
        data = [[row.get("PK"), row.get("SerialNumber"), row.get("RelStress"),
                 row.get("RelCheckpoint"), row.get("WIP"), row.get("Config"), row.get("EndTime")] for row in
                datasource]
        data.sort(key=lambda x: x[1])
        return data

    @property
    def tagger_table_data(self):
        datasource = rel_tracker_app.dbmodel.tagger_log_table_view_data
        data = [[row.get("PK"), row.get("SerialNumber"), row.get("WIP"),
                 row.get("RelStress"), row.get("RelCheckpoint"),
                 row.get("FolderGroup"), row.get("Notes"), row.get("StartTime"), row.get("EndTime")] for row in
                datasource]
        return data

    def show(self):
        self.window['-table_select-'].update(values=self.rel_table_data)
        self.window["-data_table_select-"].update(values=self.tagger_table_data)
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
            elif event == "Start Timer":
                rel_tracker_app.dbmodel.filter_set.update({"station": rel_tracker_app.station})
                if self.window['-tag_group-'].get():
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number": "Multiple"})
                rel_tracker_app.dbmodel.start_timer_data_table()
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
            elif event == "End Timer":
                rel_tracker_app.dbmodel.end_timer_data_table(self.selected_tagger_pk)
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
                print("stop timer")
            elif event.endswith("_Input-"):
                rel_tracker_app.dbmodel.filter_set.update({"serial_number": self.window["-SN_Input-"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-WIP_Input-"].get()})
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
            elif event.endswith("-ConfigPop-"):
                config_popup = config_select_vc(self.window)
                config_popup.show()
                self.window["-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
            elif event.endswith("-CkpPop-"):
                stress_popup = stress_select_vc(self.window)
                stress_popup.show()
                self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
            elif event == "Reset Filter":
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
            elif event == "-table_select-":
                # selecting SerialNumber table will set filters to selection row state
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
                    self.window["-data_table_select-"].update(values=self.tagger_table_data)
            elif event == "-data_table_select-":
                count = len(values.get('-data_table_select-'))
                if count > 0:
                    row = self.window["-data_table_select-"].get()[values.get('-data_table_select-')[0]]
                    self.selected_tagger_pk = row[0]
                    # rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-data_table_select-')})
                    # selected = self.window['-data_table_select-'].get()[
                    #     values.get('-data_table_select-')[0]]  # first one
                    # rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-data_table_select-')})
                    # sn = SnModel(selected[3], database=rel_tracker_app.dbmodel)
                    # rel_tracker_app.dbmodel.filter_set.update({
                    #     "program": sn.config.program,
                    #     "build": sn.config.build,
                    #     "config": sn.config.config_name,
                    #     "wip": sn.wip,
                    #     "stress": selected[4],
                    #     "checkpoint": selected[5],
                    #     "serial_number": sn.serial_number
                    # })
                    # self.window["-table_select-"].update(values=self.rel_table_data)

            elif event == "-show_latest0-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": False})
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_latest1-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": True})
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_current1-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": rel_tracker_app.dbmodel.station})
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
                self.window['-table_select-'].update(values=self.rel_table_data)
            elif event == "-show_current0-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": None})
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
                self.window['-table_select-'].update(values=self.rel_table_data)

            if rel_tracker_app.dbmodel.ready_to_data_tagging:
                if len(values.get('-table_select-')) == 1:
                    self.window["Start Timer"].update(disabled=False)
                else:
                    self.window["Start Timer"].update(disabled=True)
                self.window["End Timer"].update(disabled=True)
            else:
                if len(values.get('-data_table_select-')) ==1:
                    self.window["End Timer"].update(disabled=False)
                else:
                    self.window["End Timer"].update(disabled=True)
                self.window["Start Timer"].update(disabled=True)

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
        # if master:
        #     self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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
        # if master:
        #     self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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
            elif event == "RelStress":
                rel_tracker_app.dbmodel.filter_set.update({"stress": self.window["RelStress"].get()})
                self.window["RelCheckpoint"].update(value="",
                                                    values=list(rel_tracker_app.dbmodel.ckp_list_to_select))
            elif event == "-Save-":
                rel_tracker_app.dbmodel.filter_set.update({"checkpoint": self.window["RelCheckpoint"].get()})
                self.close_window()
            elif event == "-Clear-":
                rel_tracker_app.dbmodel.filter_set.update({"stress": None})
                rel_tracker_app.dbmodel.filter_set.update({"checkpoint": None})
                self.window["RelStress"].update(value=None, values=list(rel_tracker_app.dbmodel.stress_list))
                self.window["RelCheckpoint"].update(values=list(rel_tracker_app.dbmodel.ckp_list_to_select))
        self.close_window()

    def close_window(self):
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
        # if master:
        #     self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())

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
        # if master:
        #     self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_group": "Default"
                })
                self.window["-failure_mode_set-"].update(value="Default",
                                                         values=list(rel_tracker_app.dbmodel.failure_mode_group_list))

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


class stress_setup_vc:

    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_stress_setup()
        self.master = master
        # if master:
        #     self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
        rel_tracker_app.dbmodel.filter_set.update({
            "stress": None,
            "checkpoint": None
        })

    def show(self):
        self.window["-rel_stress-"].update(value="Default",
                                           values=list(rel_tracker_app.dbmodel.stress_list))

        self.window["-checkpoint_list-"].update(values=[])
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Create New Checkpoint":
                rel_tracker_app.dbmodel.filter_set.update({"stress": self.window["-rel_stress-"].get()})
                checkpoint = sg.popup_get_text("Please Provide Checkpoint Name")
                rel_tracker_app.dbmodel.insert_to_stress_table(checkpoint)
                self.window["-rel_stress-"].update(value=rel_tracker_app.dbmodel.filter_set.get("stress"),
                                                   values=list(rel_tracker_app.dbmodel.stress_list))

                self.window["-checkpoint_list-"].update(values=list(rel_tracker_app.dbmodel.ckp_list_to_select))
            elif event in ("-rel_stress-", "-rel_stress-key"):
                rel_tracker_app.dbmodel.filter_set.update({"stress": self.window["-rel_stress-"].get()})
                self.window["-checkpoint_list-"].update(values=list(rel_tracker_app.dbmodel.ckp_list_to_select))
            elif event == "-checkpoint_list-":
                rel_tracker_app.dbmodel.filter_set.update({"checkpoint": self.window["-checkpoint_list-"].get()})
            elif event == "Rename Stress":
                checkpoint_group = sg.popup_get_text("Please Provide New RelStress Name")
                if checkpoint_group:
                    # checkpoint_list = values.get("-checkpoint_list-")
                    rel_tracker_app.dbmodel.update_stress_table(stress_name=checkpoint_group,
                                                                checkpoints=None)
                    rel_tracker_app.dbmodel.filter_set.update({
                        "stress": checkpoint_group
                    })
                    self.window["-rel_stress-"].update(value=checkpoint_group,
                                                       values=list(rel_tracker_app.dbmodel.stress_list))
                    self.window["-checkpoint_list-"].update(values=list(rel_tracker_app.dbmodel.ckp_list_to_select))
            elif event == "Archive Checkpoints":
                if sg.popup_ok_cancel("you are about to remove selected checkpoints, they still exists in database but "
                                      "label as removed") == "OK":
                    checkpoint_list = values.get("-checkpoint_list-")
                    rel_tracker_app.dbmodel.delete_from_stress_table(checkpoints=checkpoint_list)
                    self.window["-checkpoint_list-"].update(values=list(rel_tracker_app.dbmodel.ckp_list_to_select))

            if len(values.get("-checkpoint_list-")) > 0:
                self.window["Archive Checkpoints"].update(disabled=False)
            else:
                self.window["Archive Checkpoints"].update(disabled=True)

        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()


class config_setup_vc:
    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_config_setup()
        self.master = master
        # if master:
        #     self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
        rel_tracker_app.dbmodel.filter_set.update({
            "program": None,
            "build": None,
            "config": None
        })

    def show(self):
        self.window["-program-"].update(value=None,
                                        values=list(rel_tracker_app.dbmodel.program_list))
        self.window["-build-"].update(value=None,
                                      values=list(rel_tracker_app.dbmodel.build_list))
        self.window["-config-"].update(values=[])
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Create Config":
                rel_tracker_app.dbmodel.filter_set.update({"program": self.window["-program-"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"build": self.window["-build-"].get()})
                config_name = sg.popup_get_text("Please Provide Config Name")
                rel_tracker_app.dbmodel.insert_to_config_table(config_name)
                self.window["-config-"].update(values=list(rel_tracker_app.dbmodel.config_list_to_select))
            elif event in ("-program-", "-program-key") :
                rel_tracker_app.dbmodel.filter_set.update({"program": self.window["-program-"].get()})
                self.window["-config-"].update(values=list(rel_tracker_app.dbmodel.config_list_to_select))
            elif event in ("-build-", "-build-key"):
                rel_tracker_app.dbmodel.filter_set.update({"build": self.window["-build-"].get()})
                self.window["-config-"].update(values=list(rel_tracker_app.dbmodel.config_list_to_select))
            elif event == "-config-":
                rel_tracker_app.dbmodel.filter_set.update({"config": self.window["-config-"].get()})
            elif event == "Rename Config":
                config_name = sg.popup_get_text(f"Please provide new name to replace {values.get('-config-')[0]}")
                rel_tracker_app.dbmodel.update_config_table(config_name)
                self.window["-config-"].update(values=list(rel_tracker_app.dbmodel.config_list_to_select))
            if self.window["-program-"].get() and self.window["-build-"].get():
                self.window["Create Config"].update(disabled=False)
            else:
                self.window["Create Config"].update(disabled=True)
            if len(self.window["-config-"].get()) == 1:
                self.window["Rename Config"].update(disabled=False)
            else:
                self.window["Rename Config"].update(disabled=True)

            print(event, values)
        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()
