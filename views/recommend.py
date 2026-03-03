# RecommendView; swipe-through recommendation cards
import threading
import requests
from io import BytesIO
from PIL import Image
import customtkinter as ctk
import theme
from utils import tag_pill

TYPE_COLOR = {"manga": theme.ACCENT, "anime": theme.MAUVE}


class RecommendView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, fg_color=theme.BG)
        self.app = app
        self._filter = "both"
        self._index = 0
        self._build_top()
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True)
        self._load_recommendations()

    def _go_back(self):
        from views.home import HomeView
        self.app.show_view(HomeView)

    def _build_top(self):
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

        active = self.app.db.get_active_media_types()
        seg_values = []
        if "manga" in active and "anime" in active:
            seg_values = ["Manga", "Anime", "Both"]
        elif "manga" in active:
            seg_values = ["Manga"]
        else:
            seg_values = ["Anime"]

        if len(seg_values) > 1:
            self._type_seg = ctk.CTkSegmentedButton(
                top, values=seg_values,
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

    def _load_recommendations(self):
        active = self.app.db.get_active_media_types()
        if self._filter == "both":
            all_recs = []
            for t in active:
                all_recs += self.app.db.get_pending_recommendations(t)
            self._recs = all_recs
        else:
            self._recs = self.app.db.get_pending_recommendations(self._filter)

        self._index = 0
        self._show_current()

    def _show_current(self):
        for w in self._content.winfo_children():
            w.destroy()

        if not self._recs or self._index >= len(self._recs):
            self._show_empty()
            return

        rec = self._recs[self._index]
        rec["tags"] = self.app.db.get_recommendation_tags(rec["mal_id"], rec["media_type"])
        self._build_card(rec)

    def _show_empty(self):
        empty = ctk.CTkFrame(self, fg_color="transparent")
        empty.pack(fill="both", expand=True)
        ctk.CTkLabel(
            self._content,
            text="No recommendations left.",
            font=ctk.CTkFont(size=16),
            text_color=theme.MUTED,
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _build_card(self, rec):
        card = ctk.CTkFrame(
            self._content,
            fg_color=theme.SURFACE0,
            corner_radius=theme.R_LG,
            border_width=1, border_color=theme.OVERLAY,
        )
        card.pack(fill="both", expand=True, padx=20, pady=16)

        # Cover image
        img_col = ctk.CTkFrame(card, fg_color="transparent")
        img_col.pack(side="left", padx=(18, 0), pady=18)
        self._img_frame = ctk.CTkFrame(
            img_col, width=160, height=220,
            fg_color=theme.SURFACE1,
            corner_radius=theme.R_MD,
        )
        self._img_frame.pack()
        self._img_frame.pack_propagate(False)
        self._cover_label = ctk.CTkLabel(
            self._img_frame, text="Loading...",
            fg_color="transparent",
            text_color=theme.MUTED,
            font=ctk.CTkFont(size=12),
        )
        self._cover_label.place(relx=0.5, rely=0.5, anchor="center")

        if rec.get("cover_url"):
            self._load_image_async(rec["cover_url"])

        # Text content
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=20, pady=18)

        # Title + type badge on same row
        title_row = ctk.CTkFrame(info, fg_color="transparent")
        title_row.pack(fill="x")
        type_color = TYPE_COLOR.get(rec["media_type"], theme.SUBTEXT)
        badge = ctk.CTkFrame(title_row, fg_color=type_color, corner_radius=theme.R_SM)
        badge.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            badge, text=rec["media_type"].upper(),
            fg_color="transparent",
            text_color=theme.BG,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).pack(padx=7, pady=3)
        ctk.CTkLabel(
            title_row, text=rec["title"],
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(side="left", fill="x")

        score_text = f"MAL Score  {rec['mal_score']}" if rec.get("mal_score") else "MAL Score  Unrated"
        ctk.CTkLabel(
            info, text=score_text,
            font=ctk.CTkFont(size=14),
            text_color=theme.ACCENT, anchor="w",
        ).pack(fill="x", pady=(3, 10))

        tags_row = ctk.CTkFrame(info, fg_color="transparent")
        tags_row.pack(fill="x", pady=(0, 12))
        for t in rec["tags"]:
            tag_pill(tags_row, t)

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
        synopsis_box.insert("1.0", rec.get("synopsis") or "No description available.")
        synopsis_box.configure(state="disabled")
        synopsis_box.pack(fill="both", expand=True)

        # Action bar
        bottom = ctk.CTkFrame(self._content, fg_color="transparent")
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
            command=lambda: self._block(rec),
        ).grid(row=0, column=0, padx=4, sticky="ew")

        ctk.CTkButton(
            bottom, text="Skip",
            height=46, corner_radius=theme.R_MD,
            fg_color="transparent",
            border_width=1, border_color=theme.OVERLAY,
            text_color=theme.SUBTEXT,
            hover_color=theme.SURFACE0,
            font=ctk.CTkFont(size=14),
            command=self._skip,
        ).grid(row=0, column=1, padx=4, sticky="ew")

        ctk.CTkButton(
            bottom, text="Save",
            height=46, corner_radius=theme.R_MD,
            fg_color=theme.ACCENT,
            hover_color="#6a9fd8",
            text_color=theme.BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._save(rec),
        ).grid(row=0, column=2, padx=4, sticky="ew")

    def _on_type_change(self, value):
        self._filter = value.lower()
        self._load_recommendations()

    def _skip(self):
        self._index += 1
        self._show_current()

    def _save(self, rec):
        self.app.db.move_recommendation_to_saved(rec["mal_id"], rec["media_type"])
        self._recs.pop(self._index)
        self._show_current()

    def _block(self, rec):
        self.app.db.add_media(
            mal_id=rec["mal_id"],
            media_type=rec["media_type"],
            title=rec["title"],
            status="blacklisted",
            tags=rec["tags"],
        )
        self.app.db.remove_recommendation(rec["mal_id"], rec["media_type"])
        self._recs.pop(self._index)
        self._show_current()

    def _load_image_async(self, url):
        def _fetch():
            try:
                response = requests.get(url, timeout=5)
                img = Image.open(BytesIO(response.content))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 220))
                self.after(0, lambda: self._cover_label.configure(image=photo, text=""))
            except Exception:
                print(f"[IMAGE] failed: {e}")
        threading.Thread(target=_fetch, daemon=True).start()