import PySimpleGUI as sg
from rel_tracker_view import *
from view_controllers import *

if __name__ == '__main__':
    app = rel_tracker_app()
    # loading_page = welcome_vc()
    initial_view = config_select_vc(None)
    initial_view.show()
    next_view = rel_log_vc()
    next_view.show()
    print(app.view_list)

