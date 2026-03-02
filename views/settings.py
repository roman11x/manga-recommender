# SettingsView; tag blacklist and active media type toggles
import customtkinter as ctk
import theme


FAKE_BLACKLISTED_TAGS = ["Hentai", "Boys Love"]


class SettingsView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self.back_to = kwargs.get("back_to", None)
        self._build_ui()

    def _go_back(self):
        if self.back_to is not None:
            if callable(self.back_to) and not isinstance(self.back_to, type):
                self.back_to()
            else:
                self.app.show_view(self.back_to)
        else:
            from views.home import HomeView
            self.app.show_view(HomeView)

    def _build_ui(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=theme.MANTLE, corner_radius=0)
        top.pack(fill="x")
        ctk.CTkButton(
            top, text="← Back", width=90, height=32,
            fg_color="transparent",
            border_width=1, border_color=theme.OVERLAY,
            text_color=theme.SUBTEXT, hover_color=theme.SURFACE0,
            corner_radius=theme.R_SM,
            command=self._go_back,
        ).pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(
            top, text="Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.TEXT,
        ).pack(side="left", padx=8)
        ctk.CTkFrame(self, height=1, fg_color=theme.OVERLAY).pack(fill="x")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=24)

        # ── Blacklisted Tags ─────────────────────────────────────────────────
        ctk.CTkLabel(
            content, text="// blacklisted tags",
            font=ctk.CTkFont(size=13),
            text_color=theme.MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(
            content, text="Blacklisted Tags",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", pady=(0, 10))

        self._tags_scroll = ctk.CTkScrollableFrame(
            content, height=120,
            fg_color=theme.SURFACE0,
            border_width=1, border_color=theme.OVERLAY,
            corner_radius=theme.R_MD,
            scrollbar_button_color=theme.SURFACE1,
            scrollbar_button_hover_color=theme.OVERLAY,
        )
        self._tags_scroll.pack(fill="x", pady=(0, 10))
        self._render_tags()

        # Add tag row
        add_row = ctk.CTkFrame(content, fg_color="transparent")
        add_row.pack(fill="x", pady=4)
        self._tag_entry = ctk.CTkEntry(
            add_row, placeholder_text="Tag name...",
            fg_color=theme.SURFACE0,
            border_color=theme.OVERLAY,
            text_color=theme.TEXT,
            placeholder_text_color=theme.MUTED,
            corner_radius=theme.R_MD,
            height=38, width=200,
            font=ctk.CTkFont(size=13),
        )
        self._tag_entry.pack(side="left", padx=(0, 8))
        self._tag_type_menu = ctk.CTkOptionMenu(
            add_row, values=["manga", "anime", "both"],
            fg_color=theme.SURFACE0,
            button_color=theme.SURFACE1,
            button_hover_color=theme.OVERLAY,
            dropdown_fg_color=theme.SURFACE0,
            dropdown_hover_color=theme.SURFACE1,
            text_color=theme.TEXT,
            corner_radius=theme.R_MD,
            width=110, height=38,
            font=ctk.CTkFont(size=13),
        )
        self._tag_type_menu.set("both")
        self._tag_type_menu.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            add_row, text="Add", width=80, height=38,
            corner_radius=theme.R_MD,
            fg_color="transparent",
            border_width=1, border_color=theme.ACCENT,
            text_color=theme.ACCENT,
            hover_color=theme.SURFACE0,
            font=ctk.CTkFont(size=13),
            command=self._add_tag,
        ).pack(side="left")

        # ── Separator ────────────────────────────────────────────────────────
        ctk.CTkFrame(content, height=1, fg_color=theme.OVERLAY).pack(fill="x", pady=22)

        # ── Active media types ───────────────────────────────────────────────
        ctk.CTkLabel(
            content, text="// recommendations",
            font=ctk.CTkFont(size=13),
            text_color=theme.MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(
            content, text="Enable Recommendations",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x", pady=(0, 10))

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x")
        for label, color in [("Manga", theme.ACCENT), ("Anime", theme.MAUVE)]:
            ctk.CTkButton(
                btn_row, text=f"{label} recommendations",
                height=44, corner_radius=theme.R_MD,
                fg_color="transparent",
                border_width=1, border_color=color,
                text_color=color,
                hover_color=theme.SURFACE0,
                font=ctk.CTkFont(size=14),
                command=lambda t=label: print(f"[SettingsView] Toggle {t}"),
            ).pack(side="left", padx=(0, 12))

    def _render_tags(self):
        for w in self._tags_scroll.winfo_children():
            w.destroy()
        for tag in FAKE_BLACKLISTED_TAGS:
            row = ctk.CTkFrame(self._tags_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row, text=tag,
                text_color=theme.TEXT,
                font=ctk.CTkFont(size=13), anchor="w",
            ).pack(side="left", padx=10, pady=6)
            ctk.CTkButton(
                row, text="Remove", width=75, height=30,
                corner_radius=theme.R_SM,
                fg_color="transparent",
                border_width=1, border_color=theme.RED,
                text_color=theme.RED,
                hover_color="#3d1f25",
                font=ctk.CTkFont(size=12),
                command=lambda t=tag: print(f"[SettingsView] Remove '{t}'"),
            ).pack(side="right", padx=8)

    def _add_tag(self):
        tag = self._tag_entry.get().strip()
        media = self._tag_type_menu.get()
        print(f"[SettingsView] Add tag '{tag}' for {media}")
