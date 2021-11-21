# this is a collection of view controllers. each view controller works on a view
# import PySimpleGUI
import shutil
import platform
from rel_tracker_view import *
# from data_model import *
import sys
import os
from file_clean_up import *


class rel_tracker_app:
    sg.user_settings_filename(path='.')
    settings = sg.user_settings()
    address = settings.get("-Local_Database-")
    station = settings.get("-Station_Name-")
    view_list = []
    sg.theme("LightGrey1")
    sg.SetOptions(font=rel_tracker_view.text_font, element_padding=(2, 2), element_size=(35, 1),
                  auto_size_buttons=True, input_elements_background_color="#f7f7f7", auto_size_text=True,
                  use_ttk_buttons=True, button_element_size=(20, 1))
    while True:
        if address:
            if DBsqlite.ok2use(address):
                dbmodel = DBsqlite(address, station=station)
                settings.update({"-Local_Database-": address})
                break
            else:
                address = sg.popup_get_file("please select database file")
                print(address)
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
        # self.show()

    def show(self):
        if sqlite3.sqlite_version_info[0] < 3:
            sg.popup_error(f"Sqlite version {sqlite3.sqlite_version}  is too low, please upgrade")
            sys.exit()
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
        self.window["-station-type-"].update(values=["RelLog Station", "FailureMode Logging Station",
                                                     "Parametric Testing Station"])
        rel_tracker_app.apply_user_settings(self.window)

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == "-WINDOW CLOSE ATTEMPTED-" or event == "Go":
                rel_tracker_app.save_user_settings(self.window)
                break
            elif event == "Save Preference":
                if self.window["-Station_Name-"].get() == "":
                    sg.popup_error("station name cannot be empty")
                else:
                    rel_tracker_app.save_user_settings(self.window)
                    sg.popup_ok("user preference saved")
            elif event == "Sync with Golden":
                gold = rel_tracker_app.settings.get("-Golden_Database-")

                user_input = sg.popup_ok_cancel(f"this operation will upload current station "
                                                f"{rel_tracker_app.station} to golden database\n"
                                                f"download other stations data to this local copy")
                if user_input == "OK":
                    rel_tracker_app.dbmodel.delete_trigger()
                    rel_tracker_app.dbmodel.sync_reference_tables(golden_db_address=gold)
                    rel_tracker_app.dbmodel.sync_rel_log_table(golden_db_address=gold)
                    rel_tracker_app.dbmodel.sync_fa_log_table(golden_db_address=gold)
                    rel_tracker_app.dbmodel.sync_tagger_log_table(golden_db_address=gold)
                    sg.popup_ok(f"sync completed. Note: only {rel_tracker_app.station} data is uploaded to golden")
                    rel_tracker_app.station = rel_tracker_app.settings.get("-Station_Name-")
                    rel_tracker_app.dbmodel.station = rel_tracker_app.station
                else:
                    sg.popup_ok("no change is made to golden and local copy")

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
            elif event == "-Golden_Database-":
                address = values.get("-Golden_Database-")
                if DBsqlite.ok2use(address):
                    self.window["-Golden_Database-"].update(value=address)
                    rel_tracker_app.settings.update({"-Golden_Database-": address})
                else:
                    self.window["-Golden_Database-"].update(value="")
                    rel_tracker_app.settings.update({"-Golden_Database-": None})
            if self.window["-Golden_Database-"].get() == self.window["-Local_Database-"].get():
                sg.popup_error("local database cannot be the same as golden database")
                self.window["-Golden_Database-"].update(value="")
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
        elif self.window["-station-type-"].get() == "Parametric Testing Station":
            rel_tracker_app.view_list.append(data_log_vc())
            rel_tracker_app.settings.update({"-first_view-": "Parametric Testing Station"})
        self.window.close()


class rel_log_vc:
    def __init__(self):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.rel_lab_station_view()
        self.complete_quit = True
        self.row_selection = None

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
                     row.get("RelCheckpoint"), row.get("StartTime"), row.get("EndTime"), row.get("Notes")] for row in
                    datasource]
            # data.sort(key=lambda x: x[3])
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
            elif event == "Show Summary":
                sg.popup_ok("Note: all failure modes are shown ")
                rel_tracker_app.dbmodel.filter_set.update({"checkpoint": None})
                rel_tracker_app.dbmodel.filter_set.update({"failure_mode": None})
                # failure_mode_selector_popup = failure_mode_summary_vc(self.window)
                # failure_mode_selector_popup.show()
                summary_popup = summary_table_vc(self.window)
                summary_popup.show()
            elif event == "Daily Report":
                today = dt.datetime.now()
                date_string = sg.popup_get_date(start_year=today.year, start_day=today.day, start_mon=today.month)
                # print (date_string)
                rel = rel_tracker_app.dbmodel.daily_rel(date_string)
                fa = rel_tracker_app.dbmodel.daily_fa(date_string)
                output_string = ""
                if rel:
                    output_string = "Today's Rel Lab update: \n"
                    for result in rel:
                        if result.get("EndTimestamp") is None:
                            printout = f'{result.get("Program")}: {result.get("SN_Count")}x ' \
                                       f'from {result.get("Config")} ' \
                                       f'Started/Resumed Rel. upcoming checkpoint: {result.get("RelStress")},' \
                                       f'{result.get("RelCheckpoint")} \n'
                        else:
                            printout = f'{result.get("Program")}: {result.get("SN_Count")}x' \
                                       f'from {result.get("Config")} ' \
                                       f'completed {result.get("RelStress")},{result.get("RelCheckpoint")}\n'
                        output_string += printout
                    output_string += "---------------------------\n\n"
                else:
                    output_string = "No New update from Rel Lab \n" \
                                    "---------------------------\n"

                if fa:
                    output_string2 = "Today's FA update: \n"
                    for result in fa:
                        printout = f'{result.get("SerialNumber")} ({result.get("Config")}) failed at ' \
                                   f'{result.get("RelStress")},{result.get("RelCheckpoint")} with failure mode:' \
                                   f'{result.get("FailureMode")}\n ' \
                                   f'Detail: {result.get("FA_Details")} \n'
                        output_string2 += printout + "---------------------------\n"
                else:
                    output_string2 = "No FA update from FA Lab \n"
                daily_report_popup = daily_report_vc(self.window, output_string + output_string2)
                daily_report_popup.show()

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
                    self.row_selection = None
                    self.window["-New-SN_Input-"].update(value="")
                    # self.window["-WIP_Input-"].update(value="FA")
                    rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
            elif event == "Add":
                user_input = sg.popup_ok_cancel(f"You are about to insert "
                                                f"{len(rel_tracker_app.dbmodel.filter_set.get('serial_number_list'))}"
                                                f" units from {rel_tracker_app.dbmodel.filter_set.get('config')}"
                                                f" to {rel_tracker_app.dbmodel.stress_str} ")
                if user_input == "OK":
                    rel_tracker_app.dbmodel.filter_set.update(
                        {
                            "station": rel_tracker_app.settings.get("-Station_Name-"),
                            "note": values.get("-New-Note-")
                        }
                    )
                    rel_tracker_app.dbmodel.insert_new_to_rel_log_table()
                    print(f"{len(rel_tracker_app.dbmodel.filter_set.get('serial_number_list'))}"
                          f" units from {rel_tracker_app.dbmodel.filter_set.get('config')}"
                          f" added to {rel_tracker_app.dbmodel.stress_str} ")
                    self.window['-table_select-'].update(values=self.table_data)
                    self.row_selection = None
                    self.window["-New-SN_Input-"].update(value="")
                    rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
                    print("window refreshed")
                else:
                    sg.popup_ok("User Abort")

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
                self.row_selection = None
                self.window["-New-SN_Input-"].update(value="")
                rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())

            elif event == "CheckIn":
                # print(event,values)
                # print(values.get("-Note-"))
                rel_tracker_app.dbmodel.filter_set.update(
                    {
                        "station": rel_tracker_app.settings.get("-Station_Name-"),
                        "note": values.get("-Note-")
                    }
                )
                stress_popup = stress_select_vc(self.window)
                stress_popup.show()
                if rel_tracker_app.dbmodel.ready_to_checkin:
                    # print(rel_tracker_app.dbmodel.filter_set.get("note"))
                    rel_tracker_app.dbmodel.checkin_to_new_checkpoint_rellog_table()
                    # print(f"{rel_tracker_app.dbmodel.filter_set.get('serial_number_list')} " f" moved to the
                    # following checkpoint: {rel_tracker_app.dbmodel.filter_set.get('checkpoint')}")
                    rel_tracker_app.reset_window_inputs(self.window)
                    self.window['-table_select-'].update(values=self.table_data)
                    self.row_selection = None
                else:
                    print("not able to checkin")
            elif event == "Checkout":
                rel_tracker_app.dbmodel.checkout_current_checkpoint_rellog_table()
                print(f"{rel_tracker_app.dbmodel.filter_set.get('serial_number_list')} checked out "
                      f"current checkpoint")
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event == "Update":
                print (values.get("-Note-"))
                rel_tracker_app.dbmodel.filter_set.update(
                    {
                        "station": rel_tracker_app.settings.get("-Station_Name-"),
                        "note": values.get("-Note-")
                    }
                )
                rel_tracker_app.dbmodel.update_current_row_rellog_table()
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": False})
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None

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
                self.row_selection = None
            elif event.endswith("-ConfigPop-"):
                config_popup = config_select_vc(self.window)
                config_popup.show()
                self.window["-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window["-New-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event.endswith("-CkpPop-"):
                stress_popup = stress_select_vc(self.window)
                stress_popup.show()
                self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window["-New-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event == "Reset":
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event == "-table_select-":
                count = len(values.get('-table_select-'))
                if count == 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": None})
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": None})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": None})
                else:
                    self.row_selection = values.get('-table_select-')
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    # selected = self.window['-table_select-'].get()[values.get('-table_select-')]
                    selected = [self.window['-table_select-'].get()[index] for index in values.get('-table_select-')]
                    selected_sn_list = [row[3] for row in selected]
                    selected_pk_list = [row[0] for row in selected]
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": selected_pk_list})
                    rel_tracker_app.dbmodel.clean_up_sn_list(",".join(selected_sn_list))
                    # rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": selected_sn_list})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    if len(selected_sn_list) == 1:
                        print(selected_sn_list, "in selection", "Note: ", str(selected[0][-1]))
                    elif len(selected_sn_list) > 1:
                        print(len(selected_sn_list), "units selected")
                    if rel_tracker_app.dbmodel.filter_set.get("update_mode"):
                        sn = SnModel(selected[0][3], database=rel_tracker_app.dbmodel)
                        rel_tracker_app.dbmodel.filter_set.update({
                            "program": sn.config.program,
                            "build": sn.config.build,
                            "config": sn.config.config_name,
                            "wip": selected[0][2],
                            "stress": selected[0][4],
                            "checkpoint": selected[0][5],
                            "serial_number": sn.serial_number,
                            "note": selected[0][-1]
                        })
                        self.window["-SN_Input-"].update(str(sn.serial_number))
                        self.window["-Config_Input-"].update(str(sn.config))
                        self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                        if rel_tracker_app.dbmodel.filter_set.get("wip") is None:
                            wip = ""
                        else:
                            wip = rel_tracker_app.dbmodel.filter_set.get("wip")
                        self.window["-WIP_Input-"].update(wip)
                        if rel_tracker_app.dbmodel.filter_set.get("note") is None:
                            note = ""
                        else:
                            note = rel_tracker_app.dbmodel.filter_set.get("note")
                        self.window["-Note-"].update(note)
            elif event == "Enter Update Mode":
                self.window['Existing Units'].select()
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": True})
                print("currently in UPDATE MODE, operating on previous record, proceed with CARE, filters stop working")
            elif event == "Exit Update Mode":
                rel_tracker_app.dbmodel.filter_set.update({"update_mode": False})
            elif event == "-show_latest0-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": False})
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event == "-show_latest1-":
                rel_tracker_app.dbmodel.display_setting.update({"show_latest": True})
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event == "-show_current1-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": rel_tracker_app.dbmodel.station})
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event == "-show_current0-":
                rel_tracker_app.dbmodel.display_setting.update({"station_filter": None})
                self.window['-table_select-'].update(values=self.table_data)
                self.row_selection = None
            elif event == "Assign WIP":
                wip = sg.popup_get_text("Please Provide New WIP, this will change current checkpoint's WIP")
                if wip is not None:
                    rel_tracker_app.dbmodel.assign_wip_row_rellog_table(wip)
                    self.window['-table_select-'].update(values=self.table_data)
                    self.row_selection = None
                    self.window["-New-SN_Input-"].update(value="")
                    rel_tracker_app.dbmodel.clean_up_sn_list(self.window["-New-SN_Input-"].get())
            elif event == "Delete":
                user_input = sg.popup_ok_cancel(f"you are about to delete "
                                                f"{len(rel_tracker_app.dbmodel.filter_set.get('selected_pks'))} rows")
                if user_input == "OK":
                    rel_tracker_app.dbmodel.delete_from_rellog_table()
                    self.window['-table_select-'].update(values=self.table_data)
                    self.row_selection = None
                else:
                    sg.popup_ok("User Abort")
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

            if rel_tracker_app.dbmodel.ready_to_add and self.window["-Tab_Selection-"].get() == "Register New Unit":
                self.window["Add"].update(disabled=False)
            else:
                self.window["Add"].update(disabled=True)

            if rel_tracker_app.dbmodel \
                    .ready_to_batch_update:
                self.window["Assign WIP"].update(disabled=False)
            else:
                self.window["Assign WIP"].update(disabled=True)
            if rel_tracker_app.dbmodel.ready_to_update:
                self.window["Update"].update(disabled=False)
            else:
                self.window["Update"].update(disabled=True)
            if rel_tracker_app.dbmodel.ready_to_checkin and self.row_selection:
                self.window["CheckIn"].update(disabled=False)
                self.window["Remove for FA"].update(disabled=False)
            else:
                self.window["CheckIn"].update(disabled=True)
                self.window["Remove for FA"].update(disabled=True)
            if rel_tracker_app.dbmodel.ready_to_checkout and self.row_selection:
                self.window["Checkout"].update(disabled=False)
            else:
                self.window["Checkout"].update(disabled=True)
            if self.row_selection:
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
        self.rel_selected_row = None
        self.fa_selected_row = None
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
        self.window["-fa_table_select-"].expand(expand_row=True)
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
            elif event == "Distribution Fitting":
                fitting_view = fitting_view_vc()
                fitting_view.show()
            elif event == "Report Failure":
                failure_mode_popup = failure_mode_vc(self.window)
                failure_mode_popup.show()
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_mode": None
                })
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.window["-fa_table_select-"].expand(expand_row=True)
                self.fa_selected_row = None
            elif event == "Edit Failure Modes":
                failure_mode_config_popup = failure_mode_config_vc(self.window)
                failure_mode_config_popup.show()
            elif event.endswith("_Input-"):
                rel_tracker_app.dbmodel.filter_set.update({"serial_number": self.window["-SN_Input-"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"wip": self.window["-WIP_Input-"].get()})
                rel_tracker_app.dbmodel.filter_set.update({"failure_mode": values.get("-Failure_Mode_Input-")})

                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.window["-fa_table_select-"].expand(expand_row=True)
                self.fa_selected_row = None
                self.rel_selected_row = None
            elif event.endswith("-ConfigPop-"):
                config_popup = config_select_vc(self.window)
                config_popup.show()
                self.window["-Config_Input-"].update(rel_tracker_app.dbmodel.config_str)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.window["-fa_table_select-"].expand(expand_row=True)
                self.fa_selected_row = None
                self.rel_selected_row = None
            elif event.endswith("-CkpPop-"):
                stress_popup = stress_select_vc(self.window)
                stress_popup.show()
                self.window["-Ckp_Input-"].update(rel_tracker_app.dbmodel.stress_str)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.window["-fa_table_select-"].expand(expand_row=True)
                self.fa_selected_row = None
                self.rel_selected_row = None
            elif event == "Show Summary":
                count = len(values.get('-table_select-'))
                if count > 0:
                    sg.popup_ok("Note: only config and stress related to table selection is shown ")
                rel_tracker_app.dbmodel.filter_set.update({"checkpoint": None})
                rel_tracker_app.dbmodel.filter_set.update({"failure_mode": None})
                failure_mode_selector_popup = failure_mode_summary_vc(self.window)
                failure_mode_selector_popup.show()
            elif event == "Reset Filter":
                rel_tracker_app.reset_window_inputs(self.window)
                self.window['-table_select-'].update(values=self.rel_table_data)
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.window["-fa_table_select-"].expand(expand_row=True)
                self.fa_selected_row = None
                self.rel_selected_row = None
            elif event == "-fa_table_select-":
                # print(values)
                try:
                    self.fa_selected_row = values.get('-fa_table_select-')
                    selected_fa_row = self.window['-fa_table_select-'].get()[values.get('-fa_table_select-')[0]]
                    print(f'{selected_fa_row[3]} FA details: {selected_fa_row[-1]}')
                except:
                    pass
            elif event == "-table_select-":
                # selecting SerialNumber table will set filters to selection row state
                count = len(values.get('-table_select-'))
                if count > 0:
                    self.rel_selected_row = values.get('-table_select-')
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": self.rel_selected_row})
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
                    self.fa_selected_row = None
            elif event == "update failure":
                self.fa_selected_row = values.get('-fa_table_select-')[0]
                rel_tracker_app.dbmodel.filter_set.update({
                    "serial_number": self.window["-fa_table_select-"].get()[self.fa_selected_row][3],
                    "stress": self.window["-fa_table_select-"].get()[self.fa_selected_row][4],
                    "checkpoint": self.window["-fa_table_select-"].get()[self.fa_selected_row][5]
                })
                failure_mode_popup = failure_mode_vc(self.window)
                failure_mode_popup.show()
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_mode": None
                })
                self.window["-fa_table_select-"].update(values=self.fa_table_data)
                self.fa_selected_row = None
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
            if self.rel_selected_row:
                self.window["Report Failure"].update(disabled=False)
            else:
                self.window["Report Failure"].update(disabled=True)
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
        self.selected_endtime = None
        self.files_list = None
        self.output_folder = rel_tracker_app.settings.get("-Output_Folder-")
        self.input_folder = rel_tracker_app.settings.get("-Input_Folder-")

    @property
    def rel_table_data(self):
        if rel_tracker_app.dbmodel.display_setting.get("show_latest"):
            datasource = rel_tracker_app.dbmodel.latest_sn_history
        else:
            datasource = rel_tracker_app.dbmodel.all_station_rel_log_table_view_data
        data = [[row.get("PK"), row.get("SerialNumber"), row.get("RelStress"),
                 row.get("RelCheckpoint"), row.get("WIP"), row.get("Config"), row.get("EndTime")] for row in
                datasource]
        # data.sort(key=lambda x: x[1])
        return data

    @property
    def tagger_table_data(self):
        datasource = rel_tracker_app.dbmodel.tagger_log_table_view_data
        data = [[row.get("PK"), row.get("SerialNumber"), row.get("WIP"),
                 row.get("RelStress"), row.get("RelCheckpoint"),
                 row.get("FolderGroup"), row.get("Notes"), row.get("StartTime")] for row in
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
            elif event == "CSV Compiler":
                file_view = file_view_vc()
                file_view.show()
            elif event == "Start Timer":
                rel_tracker_app.dbmodel.filter_set.update({"tester": self.window["-test_station-"].get().upper()})
                rel_tracker_app.dbmodel.filter_set.update({"station": rel_tracker_app.station})
                rel_tracker_app.dbmodel.checkin_to_tester_data_table()
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
            # elif event == "End Timer":
            #     rel_tracker_app.dbmodel.end_timer_data_table(self.selected_tagger_pk)
            #     self.window["-data_table_select-"].update(values=self.tagger_table_data)
            elif event == "Delete":
                # delete_from_tagger_log_table
                rel_tracker_app.dbmodel.delete_from_tagger_log_table()
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
                pass
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
                self.window["-data_table_select-"].update(values=self.tagger_table_data)
                count = len(values.get('-table_select-'))
                if count == 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": None})
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": None})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": None})
                else:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    # selected = self.window['-table_select-'].get()[values.get('-table_select-')]
                    selected = [self.window['-table_select-'].get()[index] for index in values.get('-table_select-')]
                    selected_sn_list = [row[1] for row in selected]
                    selected_pk_list = [row[0] for row in selected]
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": selected_pk_list})
                    rel_tracker_app.dbmodel.clean_up_sn_list(",".join(selected_sn_list))
                    # rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": selected_sn_list})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-table_select-')})
                    if len(selected_sn_list) == 1:
                        print(selected_sn_list, " in selection from Rel log")
                    elif len(selected_sn_list) > 1:
                        print(len(selected_sn_list), "units selected from Rel log")
            elif event == "-test_station-":
                self.window["Start Timer"].set_tooltip(f"check into test station: "
                                                       f"{self.window['-test_station-'].get()}")
            elif event == "-data_table_select-":
                self.window["-table_select-"].update(values=self.rel_table_data)
                count = len(values.get('-data_table_select-'))
                if count == 0:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": None})
                    rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": None})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": None})
                else:
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-data_table_select-')})
                    # selected = self.window['-table_select-'].get()[values.get('-table_select-')]
                    selected = [self.window['-data_table_select-'].get()[index] for index in values.get('-data_table_select-')]
                    selected_sn_list = [row[1] for row in selected]
                    selected_pk_list = [row[0] for row in selected]
                    rel_tracker_app.dbmodel.filter_set.update({"selected_pks": selected_pk_list})
                    rel_tracker_app.dbmodel.clean_up_sn_list(",".join(selected_sn_list))
                    # rel_tracker_app.dbmodel.filter_set.update({"serial_number_list": selected_sn_list})
                    rel_tracker_app.dbmodel.filter_set.update({"selected_row": values.get('-data_table_select-')})
                    if len(selected_sn_list) == 1:
                        print(selected_sn_list, " in selection from Tester Log")
                    elif len(selected_sn_list) > 1:
                        print(len(selected_sn_list), "units selected from Tester Log")

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
            if len(values.get('-table_select-')) > 0 and self.window["-test_station-"].get() != "":
                self.window["Start Timer"].update(disabled=False)
            else:
                self.window["Start Timer"].update(disabled=True)
            # self.window["End Timer"].update(disabled=True)
            # else:
            #     if len(values.get('-data_table_select-')) == 1 and self.selected_endtime is None:
            #         self.window["End Timer"].update(disabled=False)
            #     else:
            #         self.window["End Timer"].update(disabled=True)
            #     self.window["Start Timer"].update(disabled=True)
            if len(values.get("-data_table_select-")) > 0:
                self.window["Delete"].update(disabled=False)
            else:
                self.window["Delete"].update(disabled=True)

        self.close_window()

    def close_window(self):
        self.window.close()
        print("window closed")
        rel_tracker_app.save_user_settings(self.window)
        if self.complete_quit:
            sys.exit()

    @staticmethod
    def creation_date(path_to_file):
        """
        Try to get the date that a file was created, falling back to when it was
        last modified if that isn't possible.
        """
        if platform.system() == 'Windows':
            return os.path.getctime(path_to_file)
        else:
            stat = os.stat(path_to_file)
            try:
                return stat.st_birthtime
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                # so we'll settle for when its content was last modified.
                return stat.st_mtime

    @staticmethod
    def get_file_info_from_folder(folder):
        result = []
        for root, dirs, files in os.walk(folder, topdown=True):
            for name in files:
                filepath = os.path.join(root, name)
                # creation_time = os.stat(filepath).st_ctime
                creation_time = data_log_vc.creation_date(filepath)
                processed = False
                result.append((filepath, creation_time, processed))
        return result


class config_select_vc:
    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.popup_config_select()
        self.master = master
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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
                user_input = sg.popup_ok_cancel(f"you are about to remove {values.get('-highlighted_failures-')} \n"
                                                f"Note: Remove only if failure mode was added by mistake ")
                if user_input == "OK":
                    rel_tracker_app.dbmodel.delete_from_failure_log_table()
                    self.window["-failure_to_select-"].update(
                        values=rel_tracker_app.dbmodel.failure_mode_list_to_add_to_sn)
                    self.window["-highlighted_failures-"].update(values=self.existing_failure_mode_table_data)
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
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_group": "Default",
                })
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
                failure_group = sg.popup_get_text("Please Provide New Group Name, \n "
                                                  "if input already exists, selected "
                                                  "failure mode will be moved to existing group")
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
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())
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
            elif event in ("-program-", "-program-key"):
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

        self.close_window()

    def close_window(self):
        sg.user_settings_save()
        self.window.close()


class daily_report_vc:

    def __init__(self, master: sg.Window = None, content=""):
        self.master = master
        self.window = self.generate_report(content)

    def generate_report(self, content):
        layout = [
            [sg.Multiline(default_text=content, size=(100, 20), key="output")],
            [sg.CloseButton("Quit")]
        ]
        window = sg.Window('Daily Report', layout, finalize=True, modal=True)
        if self.master:
            window.TKroot.transient(master=self.master.TKroot.winfo_toplevel())
        return window

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break

    def close_window(self):
        self.window.close()


class summary_table_vc:

    def __init__(self, master: sg.Window = None):
        self.master = master
        self.all_failure_modes = list(rel_tracker_app.dbmodel.failure_mode_list)
        self.summary = StatusSummary(db=rel_tracker_app.dbmodel)
        self.configs = self.summary.get_config_obj_list()
        self.stresses = self.summary.get_stress_obj_list()
        self.stress_group = self.summary.group_by_stress()
        self.window = self.generate_tree_view()
        self.failure_modes = rel_tracker_app.dbmodel.filter_set.get("failure_mode")

    @property
    def on_going_wip_table_date(self):
        datasource = rel_tracker_app.dbmodel.on_going_wip
        if len(datasource) > 1:
            data = [[row.get("WIP"), row.get("On_going") == 1, row.get("Count"),
                     dt.datetime.fromtimestamp(row.get("Start")).strftime('%m-%d %H:%M:%S'),
                     row.get("Start")] for row in
                    datasource]
            data.sort(key=lambda x: x[3], reverse=True)
            return data
        else:
            return [["", "", "", "", ""]]

    @staticmethod
    def not_all_empty(a: list = None):
        if a:
            if len(list(filter(lambda b: b != "", a))):
                return True
            else:
                return False
        return False

    @property
    def tree_data(self):
        data = sg.TreeData()
        for stress_str, ckp_list in self.stress_group.items():
            # stress_pks = [checkpoint.id for checkpoint in ckp_list]
            # row = [self.summary.aggregated_cell_display(stress_pks, config.id) for config in self.configs]
            # if self.not_all_empty(row):
            #     data.insert(parent='', text=stress_str, key=stress_str, values=[])
            data.insert(parent='', text=stress_str, key=stress_str, values=[])
        for stress in self.stresses:
            row = [self.summary.cell_display(stress.id, config.id) for config in self.configs]
            if self.not_all_empty(row):
                data.insert(parent=stress.rel_stress, text=stress.rel_checkpoint, key=stress.id, values=row)
        return data

    def generate_tree_view(self):
        config_col = [config.config_name for config in self.configs]
        max_config_count = min(len(config_col), 8)
        tree_col_layout = [
            [sg.Tree(data=self.tree_data,
                     headings=config_col,
                     visible_column_map=[True for _ in range(max_config_count)],
                     auto_size_columns=False,
                     justification='center',
                     row_height=int(rel_tracker_view.scale * 20),
                     num_rows=15,
                     col0_width=18,
                     show_expanded=True,
                     expand_x=True,
                     expand_y=True,
                     enable_events=True,
                     key="-Tree-",
                     tooltip="note that display may not be accurate without sync with golden database,maximum 8 "
                             "configs are displayed",
                     ),
             ],
        ]
        tree_row_col = sg.Column(layout=tree_col_layout, scrollable=False, expand_y=True, expand_x=True,
                                 size=(int(1000 * rel_tracker_view.scale), int(300 * rel_tracker_view.scale)))
        layout = [[sg.Text('Current Status, fail/total (on-going)'), sg.Text("", key="-failure_mode_selection-")],
                  [tree_row_col],
                  [sg.Text("ongoing wips")],
                  [self.generate_on_going_wip_table(), sg.Stretch()],
                  [sg.VStretch()],
                  [sg.CloseButton("Quit")]]
        window = sg.Window('Quick Summary', layout, finalize=True, modal=True)
        if self.master:
            window.TKroot.transient(master=self.master.TKroot.winfo_toplevel())
        return window

    def generate_on_going_wip_table(self):
        table_col = ['WIP', 'On-going', 'unit count', 'StartTime', 'StartTimestamp']
        show_heading = [True, True, True, True, False]
        table_value = self.on_going_wip_table_date
        table_view = sg.Table(values=table_value, visible_column_map=show_heading,
                              headings=table_col,
                              expand_x=True, num_rows=10, font="Helvetica 12", header_font="Helvetica 12 bold",
                              header_background_color="white",
                              enable_events=True, key="-wip_select-", pad=(5, 10), hide_vertical_scroll=True)
        return table_view

    def show(self):
        if rel_tracker_app.dbmodel.filter_set.get('failure_mode') is None:
            display = "All"
        else:
            display = rel_tracker_app.dbmodel.filter_set.get('failure_mode')
        self.window["-failure_mode_selection-"].update(f"failure mode shown: {display}")
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break

    def close_window(self):
        self.window.close()


class failure_mode_summary_vc:
    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.all_failure_modes = list(rel_tracker_app.dbmodel.failure_mode_list)
        self.window = view.failure_mode_summary()
        self.window["-Failure_Mode_Selection-"].update(values=self.all_failure_modes)
        self.master = master
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())

    def show(self):
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "-Failure_Mode_Search-":
                keyword = values.get("-Failure_Mode_Search-")
                if keyword:
                    filtered_failure_mode = list(filter(lambda x: keyword in x, self.all_failure_modes))
                    self.window["-Failure_Mode_Selection-"].update(values=filtered_failure_mode)
                else:
                    self.window["-Failure_Mode_Selection-"].update(values=self.all_failure_modes)
            elif event == "-Failure_Mode_Selection-":
                rel_tracker_app.dbmodel.filter_set.update({"failure_mode": values.get("-Failure_Mode_Selection-")})
            elif event == "Generate Summary":
                summary_popup = summary_table_vc(self.window)
                summary_popup.show()

    def close_window(self):
        self.window.close()


class file_view_vc:

    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.file_view()
        self.master = master
        self.file = RawData()
        self.related_files = None
        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())

    def update_setting_view(self):
        self.window["start_row"].update(value=self.file.settings.get("start_row"))
        self.window["start_time"].update(values=self.file.settings.get("start_time_candi"),
                                         value=self.file.settings.get("start_time_col"))
        self.window["serial_number"].update(values=self.file.settings.get("sn_col_candi"),
                                            value=self.file.settings.get("sn_col"))
        self.window["encode"].update(value=self.file.settings.get("encode"))
        self.window["separator"].update(value=self.file.settings.get("separator"))

    def show(self):

        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Open File":
                address = self.window["-Preview-"].get()
                if address:
                    preview_data = self.file.auto_parse(address)
                    self.window["-file_preview_window-"].update(values=preview_data)
                    self.update_setting_view()
                    self.window["-folder_preview_window-"].update(values=[[""]])
            elif event == "Regen Preview":
                if self.window["skip_keywords"].get() != "":
                    skip_keywords = self.window["skip_keywords"].get().split(",")
                else:
                    skip_keywords = None
                if self.window["skip_rows"].get() != "":
                    skip_rows = self.window["skip_rows"].get().split(",")
                else:
                    skip_rows = None
                self.file.settings.update({
                    "encode": self.window["encode"].get(),
                    "start_row": self.window["start_row"].get(),
                    "end_row": -1,
                    "start_keyword": self.window["start_time"].get(),
                    "serial_number_keyword": self.window["serial_number"].get(),
                    "separator": self.window["separator"].get(),
                    "skip_keywords": skip_keywords,
                    "skip_rows": skip_rows,
                    "timestamp_format": self.window["timestamp_format"].get()
                })
                # print(self.file.settings)
                if self.window["-Preview-"].get() != "":
                    preview_data = self.file.auto_parse(self.window["-Preview-"].get())
                    self.window["-file_preview_window-"].update(values=preview_data)
                    self.update_setting_view()
                    self.window["-folder_preview_window-"].update(values=[[""]])
            elif event == "Scan Folder":
                folder = values.get("-Folder_to_Scan-")
                if folder:
                    file_list = [file[0] for file in data_log_vc.get_file_info_from_folder(folder)]
                    result = self.file.search_match_in_files(file_list)
                    self.related_files = result
                    self.window["-folder_preview_window-"].update(values=result)
            elif event == "Decode and Combine":
                result = self.file.concat_matching_files(self.related_files, rel_tracker_app.dbmodel)
                folder = sg.popup_get_folder("Please provide folder where output will be saved")
                file = os.path.join(folder, str(dt.datetime.now().date()) + "output.csv")
                if file:
                    if isinstance(result, pd.DataFrame):
                        with open(file, "w") as f:
                            result.to_csv(path_or_buf=f, index=False, line_terminator="\n")
                            # result.to_csv()
                    sg.popup_ok(f'decoded file has been saved as {str(dt.datetime.now().date()) + "output.csv"} ')
        self.close_window()

    def close_window(self):
        self.window.close()


class fitting_view_vc:

    def __init__(self, master: sg.Window = None):
        view = rel_tracker_view(rel_tracker_app.settings)
        self.window = view.fitting_view()
        self.master = master
        self.summary = StatusSummary(db=rel_tracker_app.dbmodel)
        self.stress_table_data = self.get_stress_table_data()
        self.config_table_data = self.get_config_table_data()

        if master:
            self.window.TKroot.transient(master=master.TKroot.winfo_toplevel())

    @property
    def config_grouping(self):
        if isinstance(self.config_table_data, list):
            return {row[0]: row[-1] for row in self.config_table_data}

    @property
    def stress_para_a(self):
        if isinstance(self.stress_table_data, list):
            print("this is run")
            return {row[0]: row[-2] for row in self.stress_table_data}

    @property
    def stress_para_b(self):
        if isinstance(self.stress_table_data, list):
            print("this is run")
            return {row[0]: row[-1] for row in self.stress_table_data}

    @property
    def stress_value(self):
        if isinstance(self.stress_table_data, list):
            print("this is run")
            return {row[0]: row[-3] for row in self.stress_table_data}

    def get_config_table_data(self):
        configs = self.summary.get_config_obj_list()
        if len(configs) > 0:
            return [[config.id, config.program, config.build, config.config_name, None] for config in configs]
        else:
            return None

    def get_stress_table_data(self):
        stresses = self.summary.get_stress_obj_list()
        if len(stresses) > 0:
            return [[stress.id, stress.rel_stress, stress.rel_checkpoint, None, None, None] for stress in stresses]
        else:
            return None

    @property
    def selected_configs(self):
        selected = list(filter(lambda x: x[-1], self.config_table_data))
        if len(selected) == 0:
            return self.config_table_data
        else:
            return selected

    @property
    def selected_stress(self):
        selected = list(filter(lambda x: x[3], self.stress_table_data))
        if len(selected) == 0:
            return None
        else:
            return selected

    def get_config_group(self, sn):

        pass

    def show(self):
        self.window["-config_table-"].update(values=self.config_table_data)
        self.window["-stress_table-"].update(values=self.stress_table_data)
        self.window["-failure_mode_set-"].update(value="Default",
                                                 values=list(rel_tracker_app.dbmodel.failure_mode_group_list))
        rel_tracker_app.dbmodel.filter_set.update({"failure_group": self.window["-failure_mode_set-"].get()})
        self.window["-failure_to_select-"].update(values=list(rel_tracker_app.dbmodel.failure_mode_list))
        while True:  # the event loop
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == "Update Grouping":
                group = sg.popup_get_text("Group Name")
                if group:
                    rows = values.get("-config_table-")
                    for row in rows:
                        self.config_table_data[row][-1] = group.upper()
                    self.window["-config_table-"].update(values=self.config_table_data)
            elif event == "Update Checkpoint Value":
                if len(values.get("-stress_table-")) == 1:
                    checkpoint = self.stress_table_data[values.get("-stress_table-")[0]][2]
                    default = StatusSummary.get_number(checkpoint)
                    number = sg.popup_get_text("Please input numeric value for the checkpoint", default_text=default)
                    self.stress_table_data[values.get("-stress_table-")[0]][3] = number
                    self.window["-stress_table-"].update(values=self.stress_table_data)
            elif event == "-failure_mode_set-":
                rel_tracker_app.dbmodel.filter_set.update({"failure_group": self.window["-failure_mode_set-"].get()})
                self.window["-failure_to_select-"].update(values=list(rel_tracker_app.dbmodel.failure_mode_list))
            elif event == "Update Data Table":
                rel_tracker_app.dbmodel.filter_set.update({
                    "failure_mode": self.window["-failure_to_select-"].get()
                })
                stress_pk_list = [row[0] for row in self.stress_table_data]
                config_pk_list = [row[0] for row in self.config_table_data]
                selected_sn = rel_tracker_app.dbmodel.get_selected_sn(stress_pk_list=stress_pk_list,
                                                                      config_pk_list=config_pk_list)
                # now let's convert selected_sn to the data table
                # result = [rel_tracker_app.dbmodel.weibull_output(sn.serial_number) for sn in selected_sn]
                result = []
                config_group_dict = self.config_grouping
                stress_value_dict = self.stress_value
                stress_para_a_dict = self.stress_para_a
                stress_para_b_dict = self.stress_para_b
                for sn in selected_sn:
                    weibull_output = rel_tracker_app.dbmodel.weibull_output(sn.serial_number)
                    row = [sn.serial_number, sn.config.program, sn.config.build, sn.config.config_name,
                           config_group_dict.get(sn.config.id),
                           StressModel(weibull_output[1], rel_tracker_app.dbmodel).rel_checkpoint,
                           StressModel(weibull_output[2], rel_tracker_app.dbmodel).rel_checkpoint, weibull_output[3],
                           stress_value_dict.get(weibull_output[1]), stress_value_dict.get(weibull_output[2]),
                           stress_para_a_dict.get(weibull_output[2]), stress_para_b_dict.get(weibull_output[2])]
                    result.append(row)

                print(result)

            if self.selected_stress and len(values.get("-failure_to_select-")) > 0:
                self.window["Update Data Table"].update(disabled=False)
            else:
                self.window["Update Data Table"].update(disabled=True)
        self.close_window()

    def close_window(self):
        self.window.close()
