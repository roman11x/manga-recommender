import customtkinter as ctk
import theme

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MediaApp(ctk.CTk):
    def __init__(self, db, client, first_run=False):
        super().__init__()
        self.db = db
        self.client = client
        self.configure(fg_color=theme.BG)
        self.title("Manga & Anime Recommender")
        self.geometry("900x600")
        self.minsize(800, 500)
        # Start maximised — try several methods for cross-platform compatibility
        self.after(100, self._maximize)
        self.current_view = None
        from views.onboarding import OnboardingView
        from views.home import HomeView
        self.show_view(OnboardingView if first_run else HomeView)


    def _maximize(self):
        try:
            self.state('zoomed')            # Windows + macOS Tk 8.6+
        except Exception:
            try:
                self.attributes('-zoomed', True)   # Linux X11
            except Exception:
                w, h = self.winfo_screenwidth(), self.winfo_screenheight()
                self.geometry(f"{w}x{h}+0+0")     # universal fallback

    def show_view(self, view_class, **kwargs):
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = view_class(self, **kwargs)
        self.current_view.pack(fill="both", expand=True)












