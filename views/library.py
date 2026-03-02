# LibraryView; browsable read/reading watch/watching list
import customtkinter as ctk
import theme




STATUS_DISPLAY = {
    "consumed":        ("Completed",     theme.GREEN),
    "consuming":       ("In Progress",   theme.ACCENT),
    "plan_to_consume": ("Plan to Watch", theme.YELLOW),
    "blacklisted":     ("Blacklisted",   theme.RED),
}

TYPE_COLOR = {"manga": theme.ACCENT, "anime": theme.MAUVE}


class LibraryView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self.back_to = kwargs.get("back_to", None)
        self._filter = "All"
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
            top, text="My Library",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.TEXT,
        ).pack(side="left", padx=8)
        seg = ctk.CTkSegmentedButton(
            top, values=["All", "Manga", "Anime"],
            fg_color=theme.SURFACE0,
            selected_color=theme.ACCENT,
            unselected_color=theme.SURFACE0,
            text_color=theme.TEXT,
            font=ctk.CTkFont(size=13),
            command=self._on_filter,
        )
        seg.set("All")
        seg.pack(side="right", padx=16)
        ctk.CTkFrame(self, height=1, fg_color=theme.OVERLAY).pack(fill="x")

        # Entry count
        count_lbl = ctk.CTkFrame(self, fg_color="transparent")
        count_lbl.pack(fill="x", padx=20, pady=(12, 0))
        ctk.CTkLabel(
            count_lbl,
            text=f"// {len(self.app.db.get_all_media())} entries",
            font=ctk.CTkFont(size=12),
            text_color=theme.MUTED,
        ).pack(side="left")

        # Scrollable list
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BG,
            scrollbar_button_color=theme.SURFACE1,
            scrollbar_button_hover_color=theme.OVERLAY,
        )
        self._scroll.pack(fill="both", expand=True, padx=16, pady=8)
        self._render_entries()

    def _on_filter(self, value):
        self._filter = value
        self._render_entries()

    def _render_entries(self):
        if not hasattr(self, "_open_actions"):
            self._open_actions = None
        for w in self._scroll.winfo_children():
            w.destroy()

        filtered = [
            e for e in self.app.db.get_all_media()
            if self._filter == "All" or e["media_type"] == self._filter.lower()
        ]
        if not filtered:
            ctk.CTkLabel(
                self._scroll, text="No entries found.",
                text_color=theme.MUTED, font=ctk.CTkFont(size=14),
            ).pack(pady=28)
            return

        for entry in filtered:
            row = ctk.CTkFrame(
                self._scroll,
                fg_color=theme.SURFACE0,
                corner_radius=theme.R_MD,
                border_width=1, border_color=theme.OVERLAY,
                cursor="hand2",
            )
            row.pack(fill="x", pady=5)
            if hasattr(self, "_open_actions") and self._open_actions == entry["mal_id"]:
                self._render_actions(self._scroll, entry)
            row.bind("<Button-1>", lambda e, en=entry: self._toggle_actions(en))

            # Media-type badge
            type_color = TYPE_COLOR.get(entry["media_type"], theme.SUBTEXT)
            badge_frame = ctk.CTkFrame(row, fg_color=type_color, corner_radius=theme.R_SM)
            badge_frame.pack(side="left", padx=(14, 10), pady=12)
            ctk.CTkLabel(
                badge_frame,
                text=entry["media_type"].upper(),
                fg_color="transparent",
                text_color=theme.BG,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).pack(padx=7, pady=3)

            # Title
            ctk.CTkLabel(
                row,
                text=entry["title"],
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=theme.TEXT, anchor="w",
            ).pack(side="left", fill="x", expand=True)

            # Liked star
            if entry.get("liked") == 1:
                ctk.CTkLabel(
                    row, text="★",
                    text_color=theme.YELLOW,
                    font=ctk.CTkFont(size=16),
                ).pack(side="right", padx=4)

            # Status badge
            status_text, status_color = STATUS_DISPLAY.get(
                entry["status"], (entry["status"], theme.SUBTEXT)
            )
            status_frame = ctk.CTkFrame(row, fg_color=theme.SURFACE1, corner_radius=theme.R_SM)
            status_frame.pack(side="right", padx=14, pady=12)
            ctk.CTkLabel(
                status_frame,
                text=status_text,
                fg_color="transparent",
                text_color=status_color,
                font=ctk.CTkFont(size=12),
            ).pack(padx=9, pady=3)

    def _toggle_actions(self, entry):
        # If this entry's panel is already open, close it
        if hasattr(self, "_open_actions") and self._open_actions == entry["mal_id"]:
            self._open_actions = None
            self._render_entries()
            return

        self._open_actions = entry["mal_id"]
        self._render_entries()

    def _render_actions(self, parent, entry):
        panel = ctk.CTkFrame(
            parent,
            fg_color=theme.MANTLE,
            corner_radius=theme.R_MD,
            border_width=1, border_color=theme.OVERLAY,
        )
        panel.pack(fill="x", pady=(0, 5))

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=10)

        for label, status, color in [
            ("Completed", "consumed", theme.GREEN),
            ("In Progress", "consuming", theme.ACCENT),
            ("Plan to Read", "plan_to_consume", theme.YELLOW),
        ]:
            ctk.CTkButton(
                btn_row, text=label,
                height=34, corner_radius=theme.R_SM,
                fg_color="transparent",
                border_width=1, border_color=color,
                text_color=color,
                hover_color=theme.SURFACE0,
                font=ctk.CTkFont(size=12),
                command=lambda s=status, e=entry: self._set_status(e, s),
            ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="Remove",
            height=34, corner_radius=theme.R_SM,
            fg_color="transparent",
            border_width=1, border_color=theme.RED,
            text_color=theme.RED,
            hover_color="#3d1f25",
            font=ctk.CTkFont(size=12),
            command=lambda e=entry: self._remove_entry(e),
        ).pack(side="right")

    def _set_status(self, entry, status):
        self.app.db.update_status(entry["mal_id"], entry["media_type"], status)
        self._open_actions = None
        self._render_entries()

    def _remove_entry(self, entry):
        self.app.db.delete_media(entry["mal_id"], entry["media_type"])
        self._open_actions = None
        self._render_entries()