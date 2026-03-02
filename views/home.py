# HomeView; main menu
import customtkinter as ctk
import theme


def _bind_recursive(widget, callback):
    """Bind a click callback to a widget and every descendant."""
    widget.bind("<Button-1>", callback)
    for child in widget.winfo_children():
        _bind_recursive(child, callback)


class HomeView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self._build_sidebar()
        self._build_main()

    # ── Sidebar ──────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=theme.MANTLE, width=230, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkFrame(sidebar, width=1, fg_color=theme.OVERLAY, corner_radius=0).pack(
            side="right", fill="y"
        )

        s = ctk.CTkFrame(sidebar, fg_color="transparent")
        s.pack(fill="both", expand=True, padx=28)

        ctk.CTkLabel(
            s, text="Manga",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=theme.ACCENT, anchor="w",
        ).pack(anchor="w", pady=(50, 0))
        ctk.CTkLabel(
            s, text="& Anime",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            s, text="Recommender",
            font=ctk.CTkFont(size=15),
            text_color=theme.SUBTEXT, anchor="w",
        ).pack(anchor="w", pady=(4, 20))

        bar = ctk.CTkFrame(s, height=3, width=52, fg_color=theme.ACCENT, corner_radius=2)
        bar.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            s, text="discover your\nnext obsession",
            font=ctk.CTkFont(size=13),
            text_color=theme.MUTED,
            justify="left", anchor="w",
        ).pack(anchor="w")

        ctk.CTkFrame(s, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkLabel(
            s, text="─" * 14,
            font=ctk.CTkFont(size=10),
            text_color=theme.OVERLAY, anchor="w",
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            s, text="Jikan / MAL  •  v0.1",
            font=ctk.CTkFont(size=11),
            text_color=theme.MUTED, anchor="w",
        ).pack(anchor="w", pady=(0, 28))

    # ── Nav cards ────────────────────────────────────────────────────────────

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        # Reduced pady so all 4 cards always fit at minimum window height
        main.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        tiles = [
            ("Get Recommendations", "find your next read or watch",   theme.ACCENT, self._go_recommend),
            ("My Library",          "browse your collection",          theme.MAUVE,  self._go_library),
            ("Add Title",           "search and add a title manually", theme.GREEN,  self._go_add),
            ("Settings",            "manage tags and preferences",     theme.PEACH,  self._go_settings),
        ]
        for title, desc, color, cmd in tiles:
            self._nav_card(main, title, desc, color, cmd)

    def _nav_card(self, parent, title, description, accent, cmd):
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.SURFACE0,
            corner_radius=theme.R_LG,
            border_width=1, border_color=accent,
            cursor="hand2",
        )
        card.pack(fill="x", pady=4)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=22, pady=14)

        title_lbl = ctk.CTkLabel(
            content, text=title,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=accent, anchor="w",
        )
        title_lbl.pack(fill="x")

        desc_lbl = ctk.CTkLabel(
            content, text=description,
            font=ctk.CTkFont(size=13),
            text_color=theme.MUTED, anchor="w",
        )
        desc_lbl.pack(fill="x")

        arrow = ctk.CTkLabel(
            card, text="→",
            font=ctk.CTkFont(size=20),
            text_color=accent,
        )
        arrow.place(relx=0.975, rely=0.5, anchor="e")

        cb = lambda e, fn=cmd: fn()
        _bind_recursive(card, cb)

    def _go_recommend(self):
        from views.recommend import RecommendView
        self.app.show_view(RecommendView)

    def _go_library(self):
        from views.library import LibraryView
        self.app.show_view(LibraryView)

    def _go_add(self):
        from views.add import AddView
        self.app.show_view(AddView)

    def _go_settings(self):
        from views.settings import SettingsView
        self.app.show_view(SettingsView)
