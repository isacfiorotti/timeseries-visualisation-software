import tkinter as tk
import squarify # reference in work

class TreemapView(tk.Frame):
    def __init__(self, parent, relation_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.data = data (add param to __init__)
        self.parent = parent
        self.relation_manager = relation_manager
        self.nodes = {}
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill='both', expand=True)
        self.bind('<Configure>', self.on_resize)

    def on_resize(self, event):

        data = self.relation_manager.get_node_counts()
        labels = self.relation_manager.get_nodes()
        colors = ["red", "blue", "green", "purple", "orange"]

        self.width = event.width
        self.height = event.height
        self.canvas.config(width=self.width, height=self.height)

        norm_data = squarify.normalize_sizes(data, self.width, self.height)
        rects = squarify.squarify(norm_data, 0, 0, self.width, self.height)

        self.create_treemap(rects, labels, colors)

    def create_treemap(self, rects, labels, colors):
        self.canvas.delete("all")  # Clear the canvas before drawing
        
        for rect, label, color in zip(rects, labels, colors):
            x0, y0, x1, y1 = rect['x'], rect['y'], rect['x'] + rect['dx'], rect['y'] + rect['dy']
            node_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white")
            self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, fill="black")
            
            self.nodes[label] = {'color':color}

            self.canvas.tag_bind(node_id, '<Button-1>', lambda event, label=label: self.on_click(event, label))
            self.canvas.tag_bind(node_id, '<Enter>', lambda event, label=label: self.on_enter(event, label))

    def set_vis_mediator(self, vis_mediator):
        self.vis_mediator = vis_mediator

    def on_click(self, event, label):
        self.vis_mediator.on_treemap_click()

    def on_enter(self, event, label):
        color = self.nodes[label]['color']
        self.vis_mediator.on_treemap_enter(label, color)
