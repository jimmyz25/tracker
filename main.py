from data_model import DBsqlite
from view_controllers import rel_tracker_app, welcome_vc, rel_log_vc, fa_log_vc, data_log_vc
from rel_tracker_view import *
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1]:
            new_address = sys.argv[1]
            if DBsqlite.ok2use(new_address):
                sg.user_settings().update({"-Local_Database-": new_address})
                sg.popup_ok("ok to use, loading app may take a few sec")
            else:
                sg.popup_ok("cannot open this file with AppleBerry")
                sys.exit()
        else:
            sys.exit()
    else:
        sg.popup_ok("loading, please be patient")

    app = rel_tracker_app()
    rel_tracker_app.reset_app_class()

    loading_page = welcome_vc()
    loading_page.show()
    first_view_setting = sg.user_settings().get("-first_view-")
    if first_view_setting:
        if first_view_setting == "RelLog Station":
            rel_tracker_app.view_list.append(rel_log_vc())
        elif first_view_setting == "FailureMode Logging Station":
            rel_tracker_app.view_list.append(fa_log_vc())
        elif first_view_setting == "Parametric Testing Station":
            rel_tracker_app.view_list.append(data_log_vc())
    else:
        rel_tracker_app.view_list.append(rel_log_vc())
    while True:
        if len(app.view_list) == 0:
            break
        else:
            next_view = app.view_list.pop()
            next_view.show()
    # # sys.exit()
