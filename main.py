from view_controllers import *

if __name__ == '__main__':
    app = rel_tracker_app()
    loading_page = welcome_vc()
    first_view_setting = rel_tracker_app.settings.get("-first_view-")
    if first_view_setting:
        if first_view_setting == "RelLog Station":
            rel_tracker_app.view_list.append(rel_log_vc())
        elif first_view_setting == "FailureMode Logging Station":
            rel_tracker_app.view_list.append(fa_log_vc())
        elif first_view_setting == "Data Tagging":
            rel_tracker_app.view_list.append(data_log_vc())
    else:
        rel_tracker_app.view_list.append(rel_log_vc())
    while True:
        if len(app.view_list) == 0:
            break
        else:
            next_view = app.view_list.pop()
            next_view.show()
    # sys.exit()


