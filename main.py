import PySimpleGUI as sg
from rel_tracker_view import *
from view_controllers import *

if __name__ == '__main__':
    app = rel_tracker_app()
    loading_page = welcome_vc()
    initial = rel_log_vc()
    app.view_list.append(initial)
    while True:
        if len(app.view_list) == 0:
            break
        else:
            next_view = app.view_list.pop()
            next_view.show()
    sys.exit()


