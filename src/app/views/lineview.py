import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Slider
import ast


class LineView(tk.Frame):
    def __init__(self, parent, data_mediator, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas_frame = tk.Frame(self)  # Frame for the canvas
        self.canvas_frame.pack(fill='both', expand=True)
        self.fig = None
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.data_mediator = data_mediator
        self.toolbar = NavigationToolbar2Tk(self.canvas_fig, self.canvas_frame)

        self.is_dragging = False
        self.start_drag_x = None
        self.initial_index = 0
        self.last_mouse_x = None
        self.display_count = 500
        self.scroll_speed = 2
        self.update_threshold = 5

    def generate_plot(self, data, cell_id, cell_data, colors):
        # Drop first column
        data = data.drop(data.columns[0], axis=1)
        x, y = data.iloc[:, 0], data.iloc[:, 1]

        self.data_x = np.array(x.values)
        self.data_y = np.array(y.values)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.patch.set_facecolor('#f0f0f0')
        self.fig.subplots_adjust(bottom=0.2)

        self.ax.set_title(f'Currently displaying: {cell_id}', color='grey')

        self.ax.set_ylabel(self.data_mediator.current_tab)
        self.ax.set_xlabel('Time')

        # Plot main line
        self.line, = self.ax.plot(self.data_x[:self.display_count], self.data_y[:self.display_count], lw=0.5, color='#053B50')

        signals_in_cell = self.get_signal_idxs_as_data(cell_id, cell_data)

        for i, (signal_id, signal_df) in enumerate(signals_in_cell):
            
            color = colors[i % len(colors)]

            x_signal = np.array(signal_df.loc[:, 'Time(s)'])
            y_signal = np.array(signal_df.iloc[:, 2].values, dtype=np.float64) 

            # Create a full array for y values, initialized with NaNs
            y_full = np.full_like(self.data_y, np.nan, dtype=np.float64)

            # Map x_signal to the full x range
            for x_val, y_val in zip(x_signal, y_signal):
                if x_val in self.data_x:
                    index = np.where(self.data_x == x_val)[0][0]
                    y_full[index] = y_val

            self.ax.plot(self.data_x, y_full, lw=0.5, color=color)

        self.ax.set_xlim(self.data_x[0], self.data_x[self.display_count - 1])
        self.ax.set_ylim(np.min(self.data_y[:self.display_count]), np.max(self.data_y[:self.display_count]))
        self.update_x_axis_labels(0)

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color('gray')
        self.ax.spines['left'].set_color('gray')
        self.ax.grid(color='white', linestyle='--', linewidth=0.5)
        self.ax.set_facecolor('#ADC4CE')
        self.ax.xaxis.label.set_color('grey')
        self.ax.yaxis.label.set_color('grey')
        self.ax.tick_params(axis='x', colors='grey')
        self.ax.tick_params(axis='y', colors='grey')

        self.create_lineview(self.fig)
        self.initialize_sliders()

        return self.fig


    def initialize_sliders(self):

        self.ax_slider_index = plt.axes([0.1, 0.06, 0.8, 0.02], facecolor='lightgoldenrodyellow')
        self.slider_index = Slider(self.ax_slider_index, 'Idx.', 0, len(self.data_x) - self.display_count, valinit=0, valstep=1)
        self.slider_index.label.set_fontsize(6)
        self.slider_index.valtext.set_visible(False)
        self.slider_index.on_changed(self.slider_index_update)
        self.slider_index.label.set_color('grey')
        self.slider_index.poly.set_facecolor('#ADC4CE')

        self.ax_slider_display_count = plt.axes([0.1, 0.02, 0.8, 0.02], facecolor='lightgoldenrodyellow')
        self.slider_display_count = Slider(self.ax_slider_display_count, 'Freq.', 100, len(self.data_x), valinit=self.display_count, valstep=100)
        self.slider_display_count.label.set_fontsize(6)
        self.slider_display_count.valtext.set_visible(False)
        self.slider_display_count.on_changed(self.slider_display_count_update)
        self.slider_display_count.label.set_color('grey')
        self.slider_display_count.poly.set_facecolor('#ADC4CE')

    def create_lineview(self, fig):
        self.canvas_fig.get_tk_widget().destroy()
        self.canvas_fig = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.fig = fig
        self.fig.canvas.draw_idle()
        self.toolbar.canvas = self.canvas_fig

    def update_display(self, start_index):
        if start_index < 0 or start_index + self.display_count > len(self.data_x):
            return
        new_data_x = self.data_x[start_index:start_index + self.display_count]
        new_data_y = self.data_y[start_index:start_index + self.display_count]
        self.line.set_data(np.arange(start_index, start_index + self.display_count), new_data_y)
        self.ax.set_xlim(start_index, start_index + self.display_count - 1)
        self.ax.set_ylim(np.min(new_data_y), np.max(new_data_y))
        self.update_x_axis_labels(start_index)
        self.fig.canvas.draw_idle()

    def update_x_axis_labels(self, start_index):
        end_index = start_index + self.display_count
        ticks = np.linspace(start_index, end_index - 1, num=10, dtype=int)
        self.ax.set_xticks(ticks)
        self.ax.set_xticklabels([str(self.data_x[t]) for t in ticks], ha='right', fontsize=6)

    def slider_index_update(self, val):
        start_index = int(val)
        self.update_display(start_index)

    def slider_display_count_update(self, val):
        self.display_count = int(val)
        self.slider_index.valmax = len(self.data_x) - self.display_count
        self.update_display(int(self.slider_index.val))

    def get_signal_idxs_as_data(self, cell_id, cell_data):
        signals = self.data_mediator._get_signals_in_cell(cell_id)

        signals_in_cell = []

        for signal in signals.iterrows():
            signal_id = signal[1]['signal_id']
            signal_idxs = signal[1]['signal_idxs']
            signal_idxs = ast.literal_eval(signal_idxs)
            signal_idx_data = cell_data.loc[cell_data['id'].isin(signal_idxs)]
            signals_in_cell.append((signal_id, signal_idx_data))
            
        return signals_in_cell
