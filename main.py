import PySimpleGUI as sg
from rel_tracker_view import *
from view_controllers import *

if __name__ == '__main__':
    app = rel_tracker_app()
    loading_page = welcome_vc()
    initial_view = template_view()
    print(app.view_list)

