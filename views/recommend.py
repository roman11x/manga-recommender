# RecommendView; swipe-through recommendation cards
import threading
import customtkinter as ctk
import theme


FAKE_CARD = {
    "title": "Berserk",
    "score": 9.47,
    "tags": ["Action", "Adventure", "Drama", "Fantasy", "Horror", "Supernatural"],
    "synopsis": (
        "Guts, a former mercenary now known as the 'Black Swordsman', is out for revenge. "
        "After a tumultuous childhood, he finally finds his place in the world as a member of the "
        "Band of the Hawk, a group of skilled mercenaries led by the charismatic Griffith. "
        "However, a fateful turn of events leaves Guts branded for death and hunted by demons."
    ),
}


def _tag_pill(parent, text):
    frame = ctk.CTkFrame(parent, fg_color=theme.SURFACE1, corner_radius=theme.R_SM)
    frame.pack(side="left", padx=2, pady=2)
    ctk.CTkLabel(
        frame, text=text,
        fg_color="transparent",
        text_color=theme.SUBTEXT,
        font=ctk.CTkFont(size=12),
    ).pack(padx=9, pady=4)


class RecommendView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self._build_ui()
        self._load_image_async()

    def _go_back(self):
        from views.home import HomeView
        self.app.show_view(HomeView)

    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────────────────────
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
            top, text="Recommendations",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.TEXT,
        ).pack(side="left", padx=8)
        self._type_seg = ctk.CTkSegmentedButton(
            top, values=["Manga", "Anime", "Both"],
            fg_color=theme.SURFACE0,
            selected_color=theme.ACCENT,
            unselected_color=theme.SURFACE0,
            text_color=theme.TEXT,
            font=ctk.CTkFont(size=13),
            command=self._on_type_change,
        )
        self._type_seg.set("Both")
        self._type_seg.pack(side="right", padx=16)
        ctk.CTkFrame(self, height=1, fg_color=theme.OVERLAY).pack(fill="x")

        # ── Card ─────────────────────────────────────────────────────────────
        card = ctk.CTkFrame(
            self,
            fg_color=theme.SURFACE0,
            corner_radius=theme.R_LG,
            border_width=1, border_color=theme.OVERLAY,
        )
        card.pack(fill="both", expand=True, padx=20, pady=16)

        # Cover image placeholder
        img_col = ctk.CTkFrame(card, fg_color="transparent")
        img_col.pack(side="left", padx=(18, 0), pady=18)
        self._img_frame = ctk.CTkFrame(
            img_col, width=160, height=220,
            fg_color=theme.SURFACE1,
            corner_radius=theme.R_MD,
        )
        self._img_frame.pack()
        self._img_frame.pack_propagate(False)
        ctk.CTkLabel(
            self._img_frame, text="Cover",
            fg_color="transparent",
            text_color=theme.MUTED,
            font=ctk.CTkFont(size=12),
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Text content
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=20, pady=18)

        ctk.CTkLabel(
            info,
            text=FAKE_CARD["title"],
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            info,
            text=f"MAL Score  {FAKE_CARD['score']}",
            font=ctk.CTkFont(size=14),
            text_color=theme.ACCENT, anchor="w",
        ).pack(fill="x", pady=(3, 10))

        # Tag pills
        tags_row = ctk.CTkFrame(info, fg_color="transparent")
        tags_row.pack(fill="x", pady=(0, 12))
        for tag in FAKE_CARD["tags"]:
            _tag_pill(tags_row, tag)

        synopsis_box = ctk.CTkTextbox(
            info,
            fg_color=theme.MANTLE,
            text_color=theme.SUBTEXT,
            border_color=theme.OVERLAY,
            border_width=1,
            corner_radius=theme.R_MD,
            font=ctk.CTkFont(size=13),
            wrap="word",
        )
        synopsis_box.insert("1.0", FAKE_CARD["synopsis"])
        synopsis_box.configure(state="disabled")
        synopsis_box.pack(fill="both", expand=True)

        # ── Bottom action bar ────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=(0, 18))
        bottom.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            bottom, text="Block",
            height=46, corner_radius=theme.R_MD,
            fg_color="transparent",
            border_width=1, border_color=theme.RED,
            text_color=theme.RED,
            hover_color="#3d1f25",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: print("[RecommendView] Block"),
        ).grid(row=0, column=0, padx=4, sticky="ew")

        ctk.CTkButton(
            bottom, text="Skip",
            height=46, corner_radius=theme.R_MD,
            fg_color="transparent",
            border_width=1, border_color=theme.OVERLAY,
            text_color=theme.SUBTEXT,
            hover_color=theme.SURFACE0,
            font=ctk.CTkFont(size=14),
            command=lambda: print("[RecommendView] Skip"),
        ).grid(row=0, column=1, padx=4, sticky="ew")

        ctk.CTkButton(
            bottom, text="Save",
            height=46, corner_radius=theme.R_MD,
            fg_color=theme.ACCENT,
            hover_color="#6a9fd8",
            text_color=theme.BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: print("[RecommendView] Save"),
        ).grid(row=0, column=2, padx=4, sticky="ew")

    def _on_type_change(self, value):
        print(f"[RecommendView] Filter: {value}")

    def _load_image_async(self):
        def _fetch():
            pass  # Phase 6: fetch cover, then self.after(0, callback)
        threading.Thread(target=_fetch, daemon=True).start()
