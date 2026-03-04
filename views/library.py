# LibraryView; browsable read/reading/watch/watching list
import customtkinter as ctk
import theme

TYPE_COLOR = {"manga": theme.ACCENT, "anime": theme.MAUVE}


def _bind_recursive(widget, callback):
    widget.bind("<Button-1>", callback)
    for child in widget.winfo_children():
        _bind_recursive(child, callback)


class LibraryView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self.back_to = kwargs.get("back_to", None)
        self._filter = "All"
        self._open_key = None       # (mal_id, media_type) of open action panel
        self._entries_cache = None
        self._action_panels = {}    # (mal_id, media_type) -> (row_widget, panel_widget)
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

        count_row = ctk.CTkFrame(self, fg_color="transparent")
        count_row.pack(fill="x", padx=20, pady=(12, 0))
        self._count_label = ctk.CTkLabel(
            count_row, text="",
            font=ctk.CTkFont(size=12),
            text_color=theme.MUTED,
        )
        self._count_label.pack(side="left")

        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BG,
            scrollbar_button_color=theme.SURFACE1,
            scrollbar_button_hover_color=theme.OVERLAY,
        )
        self._scroll.pack(fill="both", expand=True, padx=16, pady=8)
        self._load_and_render()

    # ── Data ─────────────────────────────────────────────────────────────────

    def _load_and_render(self):
        """Fetch fresh data from DB, then render."""
        library = self.app.db.get_all_media()
        saved_recs = [
            {
                "mal_id":     r["mal_id"],
                "media_type": r["media_type"],
                "title":      r["title"],
                "status":     "plan_to_consume",
                "liked":      None,
                "is_saved_rec": True,
            }
            for r in self.app.db.get_saved_recommendations()
        ]
        self._entries_cache = [{**e, "is_saved_rec": False} for e in library] + saved_recs
        self._count_label.configure(text=f"// {len(self._entries_cache)} entries")
        self._render_entries()

    def _on_filter(self, value):
        self._filter = value
        self._open_key = None
        self._render_entries()

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_entries(self):
        """Destroy and recreate all row widgets; pre-build (but don't pack) action panels."""
        for w in self._scroll.winfo_children():
            w.destroy()
        self._action_panels = {}

        filtered = [
            e for e in (self._entries_cache or [])
            if self._filter == "All" or e["media_type"] == self._filter.lower()
        ]

        if not filtered:
            ctk.CTkLabel(
                self._scroll, text="No entries found.",
                text_color=theme.MUTED, font=ctk.CTkFont(size=14),
            ).pack(pady=28)
            return

        for entry in filtered:
            key = (entry["mal_id"], entry["media_type"])

            row = ctk.CTkFrame(
                self._scroll,
                fg_color=theme.SURFACE0,
                corner_radius=theme.R_MD,
                border_width=1, border_color=theme.OVERLAY,
                cursor="hand2",
            )
            row.pack(fill="x", pady=5)

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

            ctk.CTkLabel(
                row,
                text=entry["title"],
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=theme.TEXT, anchor="w",
            ).pack(side="left", fill="x", expand=True)

            if entry.get("liked") == 1:
                ctk.CTkLabel(
                    row, text="★",
                    text_color=theme.YELLOW,
                    font=ctk.CTkFont(size=16),
                ).pack(side="right", padx=4)
            elif entry.get("liked") == 0:
                ctk.CTkLabel(
                    row, text="✗",
                    text_color=theme.RED,
                    font=ctk.CTkFont(size=16),
                ).pack(side="right", padx=4)

            plan_label = "Plan to Watch" if entry["media_type"] == "anime" else "Plan to Read"
            status_map = {
                "consumed":        ("Completed",   theme.GREEN),
                "consuming":       ("In Progress", theme.ACCENT),
                "plan_to_consume": (plan_label,    theme.YELLOW),
                "blacklisted":     ("Blacklisted", theme.RED),
            }
            status_text, status_color = status_map.get(
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

            # Bind after all children exist so every pixel of the row is clickable
            _bind_recursive(row, lambda e, en=entry: self._toggle_actions(en))

            # Pre-build action panel (not packed yet)
            panel = self._build_action_panel(entry)
            self._action_panels[key] = (row, panel)

        # Restore open panel if it survived the re-render
        if self._open_key and self._open_key in self._action_panels:
            row, panel = self._action_panels[self._open_key]
            panel.pack(fill="x", pady=(0, 5), after=row)

    def _build_action_panel(self, entry):
        """Build the action panel widget for an entry without packing it."""
        panel = ctk.CTkFrame(
            self._scroll,
            fg_color=theme.MANTLE,
            corner_radius=theme.R_MD,
            border_width=1, border_color=theme.OVERLAY,
        )
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=10)

        plan_label = "Plan to Watch" if entry["media_type"] == "anime" else "Plan to Read"

        # Liked/Disliked sub-row — hidden until "Completed" is clicked
        liked_row = ctk.CTkFrame(panel, fg_color="transparent")
        ctk.CTkLabel(
            liked_row, text="Did you like it?",
            font=ctk.CTkFont(size=13), text_color=theme.SUBTEXT,
        ).pack(side="left", padx=(0, 12))
        for lbl, val, color in [("Liked", 1, theme.GREEN), ("Disliked", 0, theme.RED)]:
            if entry.get("is_saved_rec"):
                liked_cmd = lambda v=val, e=entry: self._add_rec_to_library(e, "consumed", liked=v)
            else:
                liked_cmd = lambda v=val, e=entry: self._set_status(e, "consumed", liked=v)
            ctk.CTkButton(
                liked_row, text=lbl,
                height=34, corner_radius=theme.R_SM,
                fg_color="transparent",
                border_width=1, border_color=color,
                text_color=color,
                hover_color=theme.SURFACE0,
                font=ctk.CTkFont(size=12),
                command=liked_cmd,
            ).pack(side="left", padx=(0, 8))

        for label, status, color in [
            ("Completed",   "consumed",        theme.GREEN),
            ("In Progress", "consuming",       theme.ACCENT),
            (plan_label,    "plan_to_consume", theme.YELLOW),
        ]:
            if status == "consumed":
                cmd = lambda lr=liked_row: lr.pack(fill="x", padx=14, pady=(0, 10))
            elif entry.get("is_saved_rec"):
                cmd = lambda s=status, e=entry: self._add_rec_to_library(e, s)
            else:
                cmd = lambda s=status, e=entry: self._set_status(e, s)
            ctk.CTkButton(
                btn_row, text=label,
                height=34, corner_radius=theme.R_SM,
                fg_color="transparent",
                border_width=1, border_color=color,
                text_color=color,
                hover_color=theme.SURFACE0,
                font=ctk.CTkFont(size=12),
                command=cmd,
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
        return panel

    # ── Toggle (no full re-render) ────────────────────────────────────────────

    def _toggle_actions(self, entry):
        key = (entry["mal_id"], entry["media_type"])
        if self._open_key == key:
            _, panel = self._action_panels[key]
            panel.pack_forget()
            self._open_key = None
        else:
            if self._open_key and self._open_key in self._action_panels:
                _, old_panel = self._action_panels[self._open_key]
                old_panel.pack_forget()
            row, panel = self._action_panels[key]
            panel.pack(fill="x", pady=(0, 5), after=row)
            self._open_key = key

    # ── Actions ───────────────────────────────────────────────────────────────

    def _add_rec_to_library(self, entry, status, liked=None):
        """Move a saved recommendation into the media library."""
        existing = self.app.db.get_media(entry["mal_id"], entry["media_type"])
        if existing:
            self.app.db.update_status(entry["mal_id"], entry["media_type"], status)
            if liked is not None:
                self.app.db.update_liked(entry["mal_id"], entry["media_type"], liked)
        else:
            tags = self.app.db.get_recommendation_tags(entry["mal_id"], entry["media_type"])
            self.app.db.add_media(
                mal_id=entry["mal_id"],
                media_type=entry["media_type"],
                title=entry["title"],
                status=status,
                tags=tags,
                liked=liked,
            )
        self.app.db.remove_recommendation(entry["mal_id"], entry["media_type"])
        self._open_key = None
        self._load_and_render()

    def _set_status(self, entry, status, liked=None):
        self.app.db.update_status(entry["mal_id"], entry["media_type"], status)
        if liked is not None:
            self.app.db.update_liked(entry["mal_id"], entry["media_type"], liked)
        self._open_key = None
        self._load_and_render()

    def _remove_entry(self, entry):
        if entry.get("is_saved_rec"):
            self.app.db.remove_recommendation(entry["mal_id"], entry["media_type"])
        else:
            self.app.db.delete_media(entry["mal_id"], entry["media_type"])
        self._open_key = None
        self._load_and_render()
