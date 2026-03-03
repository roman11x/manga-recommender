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
        if not first_run:
            self.after(500, self._run_feedback_loop)

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

    def _run_feedback_loop(self):
        saved = self.db.get_saved_recommendations()
        if not saved:
            return
        self._feedback_queue = list(saved)
        self._show_feedback_dialog()

    def _show_feedback_dialog(self):
        if not self._feedback_queue:
            return

        rec = self._feedback_queue.pop(0)

        # Build modal window
        dialog = ctk.CTkToplevel(self)
        dialog.title("How was it?")
        dialog.geometry("480x280")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.lift()
        dialog.focus_force()
        dialog.configure(fg_color=theme.BG)

        # Center it over the main window
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 240
        y = self.winfo_y() + (self.winfo_height() // 2) - 140
        dialog.geometry(f"+{x}+{y}")

        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(
            content, text="Did you consume this?",
            font=ctk.CTkFont(size=13),
            text_color=theme.MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            content, text=rec["title"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=theme.TEXT, anchor="w",
            wraplength=420,
        ).pack(fill="x", pady=(0, 4))

        type_color = theme.ACCENT if rec["media_type"] == "manga" else theme.MAUVE
        ctk.CTkLabel(
            content, text=rec["media_type"].upper(),
            font=ctk.CTkFont(size=12),
            text_color=type_color, anchor="w",
        ).pack(fill="x", pady=(0, 20))

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x")

        def on_not_yet():
            dialog.destroy()
            self._show_feedback_dialog()

        def on_disliked():
            tags = self.db.get_recommendation_tags(rec["mal_id"], rec["media_type"])
            self.db.add_media(
                mal_id=rec["mal_id"],
                media_type=rec["media_type"],
                title=rec["title"],
                status="blacklisted",
                tags=tags,
                liked=0,
            )
            self.db.remove_recommendation(rec["mal_id"], rec["media_type"])
            dialog.destroy()
            self._show_feedback_dialog()

        def on_liked():
            tags = self.db.get_recommendation_tags(rec["mal_id"], rec["media_type"])
            self.db.add_media(
                mal_id=rec["mal_id"],
                media_type=rec["media_type"],
                title=rec["title"],
                status="consumed",
                tags=tags,
                liked=1,
            )
            self.db.remove_recommendation(rec["mal_id"], rec["media_type"])
            dialog.destroy()
            self._show_feedback_dialog()

        for text, color, cmd in [
            ("Not yet",  theme.OVERLAY, on_not_yet),
            ("Disliked", theme.RED,     on_disliked),
            ("Liked ★",  theme.GREEN,   on_liked),
        ]:
            ctk.CTkButton(
                btn_row, text=text,
                height=44, corner_radius=theme.R_MD,
                fg_color="transparent",
                border_width=1, border_color=color,
                text_color=color,
                hover_color=theme.SURFACE0,
                font=ctk.CTkFont(size=14),
                command=cmd,
            ).pack(side="left", padx=(0, 10))
