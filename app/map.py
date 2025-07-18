import customtkinter
from tkintermapview import TkinterMapView

customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simple Map Viewer")
        self.geometry("800x500")

        # Create map widget
        self.map_widget = TkinterMapView(self, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)

        # Set default location using coordinates (no address lookup)
        self.map_widget.set_position(35.146045315654895, 33.413104992584266)  # Berlin coordinates
        self.map_widget.set_zoom(10)

        # Add button to draw a line
        self.line_button = customtkinter.CTkButton(self, text="Add Line", command=self.add_line)
        self.line_button.pack(pady=10)

    def add_line(self):
        # Example coordinates for the line
        start_coords = (52.5200, 13.4050)  # Berlin
        end_coords = (48.8566, 2.3522)  # Paris
        self.map_widget.set_path([start_coords, end_coords])


if __name__ == "__main__":
    app = App()
    app.mainloop()
