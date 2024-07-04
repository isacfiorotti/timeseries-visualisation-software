import tkinter as tk
from app.views.lineview import LineView
from app.views.treemap import TreemapView
from app.views.gridview import GridView
from app.views.tabs import Tabs
from app.views.add_icon import AddIcon
from app.views.settings_icon import SettingsIcon
from app.controllers.vis_mediator import VisMediator


class MainWindow(tk.Frame):
    def __init__(self, parent, data_mediator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.data_mediator = data_mediator
        self.init_ui()
    
    def init_ui(self):

        #RENAME this variabel
        #window
        self.window = tk.Frame(self, background='grey')
        self.window.pack(fill='both', expand=True)

        #horizontal tab
        self.tab_frame = tk.Frame(self.window, background='#ECECEC', height=20) # tab height
        self.tab_frame.pack(fill='x')

        #plus icon
        self.add_icon = AddIcon(self.tab_frame)
        self.add_icon.pack(side='left')

        #settings icon
        self.add_icon = SettingsIcon(self.tab_frame)
        self.add_icon.pack(side='right')

        #tabs
        self.tabs = Tabs(self.tab_frame, self.data_mediator)
        self.tabs.pack(fill='both', expand=True)

        #vertical_paned_window
        self.vertical_paned_window = tk.PanedWindow(self.window, orient='vertical')
        self.vertical_paned_window.pack(fill='both', expand=True)

        #top frame
        self.top = tk.PanedWindow(self.window, orient='horizontal') # Top frame is a paned window for dividing left and right
        self.top.pack(fill='both', expand=True)
        self.vertical_paned_window.add(self.top, stretch='always')

        #grid_view
        self.grid_frame = tk.Frame(self.top)
        self.top.add(self.grid_frame, stretch='always')
        self.grid_view = GridView(self.grid_frame)
        self.grid_view.pack(fill='both', expand=True)

        #treemap
        self.treemap_frame = tk.Frame(self.top)
        self.top.add(self.treemap_frame, stretch='always')
        self.treemap = TreemapView(self.treemap_frame, self.data_mediator)
        self.treemap.pack(fill='both', expand=True)
        
        #bottom frame
        self.bottom = tk.Frame(self.window, background='light green')
        self.bottom.pack(side='bottom', fill='both', expand=True)
        self.vertical_paned_window.add(self.bottom, stretch='always')
        
        #lineview
        self.line_view = LineView(self.bottom) # put the line view into a frame
        self.line_view.pack(fill='both', expand=True)

        #vis mediator
        vis_mediator = VisMediator(self.data_mediator, self.tabs, self.treemap, self.grid_view, self.line_view)
        self.tabs.set_vis_mediator(vis_mediator)
        self.treemap.set_vis_mediator(vis_mediator)
        self.grid_view.set_vis_mediator(vis_mediator)

        

