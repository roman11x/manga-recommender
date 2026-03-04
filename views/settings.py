# SettingsView; tag blacklist and active media type toggles
import threading
import customtkinter as ctk
import theme


class SettingsView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self.back_to = kwargs.get("back_to", None)
        self._active_override = kwargs.get("active_override", None)
        self._genre_cache = {}   # {"manga": [name, ...], "anime": [name, ...]}
        self._genre_names = []   # current valid names for validation
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

        self._tag_combobox = ctk.CTkComboBox(
            add_row, values=["Loading genres..."],
            fg_color=theme.SURFACE0,
            border_color=theme.OVERLAY,
            text_color=theme.TEXT,
            button_color=theme.SURFACE1,
            button_hover_color=theme.OVERLAY,
            dropdown_fg_color=theme.SURFACE0,
            dropdown_hover_color=theme.SURFACE1,
            dropdown_text_color=theme.TEXT,
            corner_radius=theme.R_MD,
            height=38, width=240,
            font=ctk.CTkFont(size=13),
            state="disabled",
        )
        self._tag_combobox.set("Loading genres...")
        self._tag_combobox.pack(side="left", padx=(0, 8))

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
            command=self._on_type_change,
        )
        if self._active_override and len(self._active_override) == 1:
            self._tag_type_menu.set(self._active_override[0])
        else:
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

        active = self._active_override if self._active_override is not None else self.app.db.get_active_media_types()
        inactive = [t for t in ["manga", "anime"] if t not in active]

        if not inactive:
            ctk.CTkLabel(
                content, text="All media types are active.",
                text_color=theme.MUTED, font=ctk.CTkFont(size=13),
            ).pack(anchor="w")
        else:
            btn_row = ctk.CTkFrame(content, fg_color="transparent")
            btn_row.pack(fill="x")
            for media_type in inactive:
                color = theme.ACCENT if media_type == "manga" else theme.MAUVE
                ctk.CTkButton(
                    btn_row, text=f"Enable {media_type} recommendations",
                    height=44, corner_radius=theme.R_MD,
                    fg_color="transparent",
                    border_width=1, border_color=color,
                    text_color=color,
                    hover_color=theme.SURFACE0,
                    font=ctk.CTkFont(size=14),
                    command=lambda t=media_type: self._enable_type(t),
                ).pack(side="left", padx=(0, 12))

        # Kick off genre loading
        self._load_genres()

    # ── Genre loading ─────────────────────────────────────────────────────────

    def _on_type_change(self, _=None):
        self._load_genres()

    def _load_genres(self):
        media_type = self._tag_type_menu.get()

        # Serve from cache when possible
        if media_type == "both":
            if "manga" in self._genre_cache and "anime" in self._genre_cache:
                names = sorted(set(self._genre_cache["manga"]) | set(self._genre_cache["anime"]))
                self._set_genres(names)
                return
        else:
            if media_type in self._genre_cache:
                self._set_genres(self._genre_cache[media_type])
                return

        self._tag_combobox.configure(state="disabled")
        self._tag_combobox.set("Loading genres...")

        def fetch():
            try:
                if media_type == "both":
                    for t in [m for m in ("manga", "anime") if m not in self._genre_cache]:
                        genres = self.app.client.get_genres(t) or {}
                        self._genre_cache[t] = sorted(genres.keys())
                    names = sorted(set(self._genre_cache.get("manga", [])) | set(self._genre_cache.get("anime", [])))
                else:
                    genres = self.app.client.get_genres(media_type) or {}
                    self._genre_cache[media_type] = sorted(genres.keys())
                    names = self._genre_cache[media_type]
            except Exception:
                names = []
            self.after(0, lambda ns=names: self._set_genres(ns))

        threading.Thread(target=fetch, daemon=True).start()

    def _set_genres(self, names):
        self._genre_names = names
        if not names:
            self._tag_combobox.configure(values=["(unavailable)"], state="disabled")
            self._tag_combobox.set("(unavailable)")
            return
        self._tag_combobox.configure(values=names, state="normal")
        self._tag_combobox.set(names[0])

    # ── Tag management ────────────────────────────────────────────────────────

    def _enable_type(self, media_type):
        from views.onboarding import OnboardingView
        active = self.app.db.get_active_media_types()
        if media_type not in active:
            active.append(media_type)
        self.app.db.set_setting("active_media_types", ",".join(active))
        self.app.show_view(
            OnboardingView,
            step=2,
            selected_types=active,
        )

    def _render_tags(self):
        for w in self._tags_scroll.winfo_children():
            w.destroy()
        tags = self.app.db.get_all_blacklisted_tags()
        if not tags:
            ctk.CTkLabel(
                self._tags_scroll, text="No blacklisted tags.",
                text_color=theme.MUTED, font=ctk.CTkFont(size=13),
            ).pack(pady=8)
            return
        for entry in tags:
            row = ctk.CTkFrame(self._tags_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row, text=f"{entry['tag']}  —  {entry['media_type']}",
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
                command=lambda e=entry: self._remove_tag(e["tag"], e["media_type"]),
            ).pack(side="right", padx=8)

    def _add_tag(self):
        tag = self._tag_combobox.get().strip()
        if not tag or tag not in self._genre_names:
            return
        media = self._tag_type_menu.get()
        self.app.db.add_blacklisted_tag(tag, media)
        self._render_tags()

    def _remove_tag(self, tag, media_type):
        self.app.db.remove_blacklisted_tag(tag, media_type)
        self._render_tags()
