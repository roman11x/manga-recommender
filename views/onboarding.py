# OnboardingView; first-run setup flow
import customtkinter as ctk
import theme


def _bind_recursive(widget, callback):
    widget.bind("<Button-1>", callback)
    for child in widget.winfo_children():
        _bind_recursive(child, callback)


class OnboardingView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self.step = kwargs.get("step", 1)
        self.selected_types = kwargs.get("selected_types", None)
        self._build()

    def _build(self):
        if self.step == 1:
            self._build_step1()
        else:
            self._build_step2()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ── Step 1: three full-height columns ────────────────────────────────────

    def _build_step1(self):
        self._clear()

        # Header strip
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        ctk.CTkLabel(
            header, text="Welcome",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=theme.TEXT,
            anchor="center",
        ).pack(fill="x")
        ctk.CTkLabel(
            header, text="choose your focus to get started",
            font=ctk.CTkFont(size=16),
            text_color=theme.SUBTEXT,
            anchor="center",
        ).pack(fill="x")

        # Thin separator under header
        ctk.CTkFrame(self, height=1, fg_color=theme.OVERLAY).pack(fill="x")

        # Three columns filling all remaining vertical space
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="both", expand=True)

        data = [
            ("Manga", "only",  ["manga"],         "books, manhwa\n& manhua",  theme.ACCENT),
            ("Anime", "only",  ["anime"],          "series, films\n& OVAs",    theme.MAUVE),
            ("Both",  "",      ["manga", "anime"], "everything,\nno limits",   theme.GREEN),
        ]

        for i, (title, subtitle, value, blurb, accent) in enumerate(data):
            if i > 0:
                # 1 px vertical separator between columns
                ctk.CTkFrame(row, width=1, fg_color=theme.OVERLAY, corner_radius=0).pack(
                    side="left", fill="y"
                )
            self._option_card(row, title, subtitle, value, blurb, accent)

    def _option_card(self, parent, title, subtitle, value, blurb, accent):
        card = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0, cursor="hand2")
        card.pack(side="left", fill="both", expand=True)

        # Coloured top accent bar
        ctk.CTkFrame(card, height=4, fg_color=accent, corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=12)

        # ── "Select →" anchored to the bottom ───────────────────────────
        ctk.CTkLabel(
            inner, text="Select  →",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=accent,
        ).pack(side="bottom", pady=(0, 12))

        # ── Equal spacers centre title+blurb in the remaining space ─────
        ctk.CTkFrame(inner, fg_color="transparent").pack(fill="both", expand=True)

        # ── Title + "only" ──────────────────────────────────────────────
        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.pack()
        ctk.CTkLabel(
            title_row, text=title,
            font=ctk.CTkFont(size=90, weight="bold"),
            text_color=accent,
        ).pack(side="left")
        if subtitle:
            ctk.CTkLabel(
                title_row, text=f" {subtitle}",
                font=ctk.CTkFont(size=36),
                text_color=theme.SUBTEXT,
            ).pack(side="left", anchor="s", pady=(0, 16))

        # ── Blurb directly under title ──────────────────────────────────
        ctk.CTkLabel(
            inner, text=blurb,
            font=ctk.CTkFont(size=22),
            text_color=theme.MUTED,
            justify="center",
        ).pack(pady=(6, 0))

        ctk.CTkFrame(inner, fg_color="transparent").pack(fill="both", expand=True)

        fn = lambda v=value: self._select_type(v)
        _bind_recursive(card, lambda e, f=fn: f())

    def _select_type(self, value):
        self.selected_types = value
        self.step = 2
        self._build_step2()

    # ── Step 2: setup ────────────────────────────────────────────────────────

    def _build_step2(self):
        self._clear()

        type_label = {
            ("manga",):         "manga",
            ("anime",):         "anime",
            ("manga", "anime"): "manga and anime",
        }.get(tuple(self.selected_types), "media")

        type_accent = {
            ("manga",):         theme.ACCENT,
            ("anime",):         theme.MAUVE,
            ("manga", "anime"): theme.GREEN,
        }.get(tuple(self.selected_types), theme.ACCENT)

        # Top bar
        top = ctk.CTkFrame(self, fg_color=theme.MANTLE, corner_radius=0)
        top.pack(fill="x")
        ctk.CTkButton(
            top, text="← Back", width=90, height=32,
            fg_color="transparent",
            border_width=1, border_color=theme.OVERLAY,
            text_color=theme.SUBTEXT, hover_color=theme.SURFACE0,
            corner_radius=theme.R_SM,
            command=self._go_step1,
        ).pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(
            top, text="Set up your library",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.TEXT,
        ).pack(side="left", padx=8)
        ctk.CTkFrame(self, height=1, fg_color=theme.OVERLAY).pack(fill="x")

        # Two-column body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        # Left info panel
        left = ctk.CTkFrame(body, fg_color=theme.MANTLE, width=260, corner_radius=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        ctk.CTkFrame(left, width=1, fg_color=theme.OVERLAY, corner_radius=0).pack(
            side="right", fill="y"
        )
        lc = ctk.CTkFrame(left, fg_color="transparent")
        lc.pack(fill="both", expand=True, padx=28)

        ctk.CTkLabel(
            lc, text="How it works",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(anchor="w", pady=(40, 20))

        for num, text in [
            ("01", f"Add {type_label} you\nhave already finished"),
            ("02", "We learn from your\ntaste and history"),
            ("03", "Get personalised\nrecommendations"),
        ]:
            row = ctk.CTkFrame(lc, fg_color="transparent")
            row.pack(anchor="w", pady=10)
            ctk.CTkLabel(
                row, text=num,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=type_accent,
            ).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(
                row, text=text,
                font=ctk.CTkFont(size=15),
                text_color=theme.SUBTEXT,
                justify="left", anchor="w",
            ).pack(side="left")

        # Right actions panel
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=48, pady=36)

        ctk.CTkLabel(
            right,
            text=f"Add some {type_label} you've already finished\nso we can learn your taste.",
            font=ctk.CTkFont(size=15),
            text_color=theme.SUBTEXT,
            justify="left", anchor="w",
        ).pack(anchor="w", pady=(0, 28))

        def go_add():
            from views.add import AddView
            saved = list(self.selected_types)
            self.app.show_view(
                AddView,
                back_to=lambda: self.app.show_view(
                    OnboardingView, step=2, selected_types=saved
                ),
            )

        def go_settings():
            from views.settings import SettingsView
            saved = list(self.selected_types)
            self.app.show_view(
                SettingsView,
                back_to=lambda: self.app.show_view(
                    OnboardingView, step=2, selected_types=saved
                ),
                active_override=saved,
            )

        for text, cmd in [
            (f"+ Add {type_label} titles", go_add),
            ("/  Exclude tags",             go_settings),
        ]:
            ctk.CTkButton(
                right, text=text,
                height=48, corner_radius=theme.R_MD,
                fg_color=theme.SURFACE0,
                hover_color=theme.SURFACE1,
                text_color=theme.TEXT,
                font=ctk.CTkFont(size=14),
                border_width=1, border_color=theme.OVERLAY,
                anchor="w",
                command=cmd,
            ).pack(fill="x", pady=5)

        ctk.CTkFrame(right, height=1, fg_color=theme.OVERLAY).pack(fill="x", pady=28)

        # Generate button
        has_entries = self.app.db.has_consumed_liked_entries()
        count = len(self.app.db.get_all_media())
        if has_entries:
            gen_text  = f"Generate recommendations  ({count} titles added)"
            gen_fg    = theme.ACCENT
            gen_hover = "#6a9fd8"
            gen_tc    = theme.BG
            gen_state = "normal"
        else:
            gen_text  = "Generate recommendations  — add titles above first"
            gen_fg    = theme.SURFACE0
            gen_hover = theme.SURFACE0
            gen_tc    = theme.MUTED
            gen_state = "disabled"

        ctk.CTkButton(
            right, text=gen_text,
            height=50, corner_radius=theme.R_MD,
            fg_color=gen_fg, hover_color=gen_hover,
            text_color=gen_tc,
            font=ctk.CTkFont(size=14, weight="bold"),
            state=gen_state,
            command=self._generate,
        ).pack(fill="x", pady=4)

    def _go_step1(self):
        self.step = 1
        self._build_step1()

    def _generate(self):
        self.app.db.set_setting("active_media_types", ",".join(self.selected_types))
        self._show_loading()
        import threading
        from generator import generate_recommendations
        def run():

            try:
                generate_recommendations(self.app.db, self.app.client)
                print("[GEN] done, scheduling transition")
                self.app.after(0, self._on_generation_done)
            except Exception as e:
                print(f"[GEN] error: {e}")
                import traceback
                traceback.print_exc()
                self.app.after(0, self._on_generation_done)

        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _show_loading(self):
        self._clear()
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(fill="both", expand=True)
        ctk.CTkLabel(
            center,
            text="Generating recommendations...",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=theme.TEXT,
        ).place(relx=0.5, rely=0.45, anchor="center")
        ctk.CTkLabel(
            center,
            text="fetching titles from Jikan  •  this may take a moment",
            font=ctk.CTkFont(size=14),
            text_color=theme.MUTED,
        ).place(relx=0.5, rely=0.52, anchor="center")

    def _on_generation_done(self):
        print("[GEN] transitioning to HomeView")
        from views.home import HomeView
        self.app.show_view(HomeView)
