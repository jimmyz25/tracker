import PySimpleGUI as sg
from rel_tracker_view import *
from view_controllers import *

app = rel_tracker_app()
loading_page = loading_page(app)
initial_view = view_a(app)

