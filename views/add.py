# AddView; search and add manga/anime manually
import customtkinter as ctk
import theme


FAKE_RESULT = {
    "title": "Fullmetal Alchemist",
    "score": 9.08,
    "tags": ["Action", "Adventure", "Drama", "Fantasy"],
    "synopsis": (
        "After a failed alchemical ritual, brothers Edward and Alphonse Elric are left scarred. "
        "Edward loses his left leg and right arm; Alphonse loses his entire body. "
        "In a desperate attempt to restore themselves, they search for the legendary Philosopher's Stone."
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


class AddView(ctk.CTkFrame):
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
            top, text="Add Title",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.TEXT,
        ).pack(side="left", padx=8)
        self._type_seg = ctk.CTkSegmentedButton(
            top, values=["Manga", "Anime"],
            fg_color=theme.SURFACE0,
            selected_color=theme.ACCENT,
            unselected_color=theme.SURFACE0,
            text_color=theme.TEXT,
            font=ctk.CTkFont(size=13),
        )
        self._type_seg.set("Manga")
        self._type_seg.pack(side="right", padx=16)
        ctk.CTkFrame(self, height=1, fg_color=theme.OVERLAY).pack(fill="x")

        # Search bar
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=18)
        self._search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Search for a title...",
            fg_color=theme.SURFACE0,
            border_color=theme.OVERLAY,
            text_color=theme.TEXT,
            placeholder_text_color=theme.MUTED,
            corner_radius=theme.R_MD,
            height=44,
            font=ctk.CTkFont(size=14),
        )
        self._search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._search_entry.bind("<Return>", lambda _: self._do_search())
        ctk.CTkButton(
            search_row, text="Search",
            width=110, height=44,
            corner_radius=theme.R_MD,
            fg_color=theme.ACCENT,
            hover_color="#6a9fd8",
            text_color=theme.BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_search,
        ).pack(side="left")

        # Result area
        self._result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

    def _do_search(self):
        for w in self._result_frame.winfo_children():
            w.destroy()

        result = FAKE_RESULT
        card = ctk.CTkFrame(
            self._result_frame,
            fg_color=theme.SURFACE0,
            corner_radius=theme.R_LG,
            border_width=1, border_color=theme.OVERLAY,
        )
        card.pack(fill="x", pady=4)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(
            inner, text=result["title"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            inner, text=f"MAL Score  {result['score']}",
            font=ctk.CTkFont(size=14),
            text_color=theme.ACCENT, anchor="w",
        ).pack(fill="x", pady=(3, 10))

        tags_row = ctk.CTkFrame(inner, fg_color="transparent")
        tags_row.pack(fill="x", pady=(0, 10))
        for tag in result["tags"]:
            _tag_pill(tags_row, tag)

        synopsis_box = ctk.CTkTextbox(
            inner,
            height=80,
            fg_color=theme.MANTLE,
            text_color=theme.SUBTEXT,
            border_color=theme.OVERLAY,
            border_width=1,
            corner_radius=theme.R_MD,
            font=ctk.CTkFont(size=13),
            wrap="word",
        )
        synopsis_box.insert("1.0", result["synopsis"])
        synopsis_box.configure(state="disabled")
        synopsis_box.pack(fill="x", pady=(0, 14))

        # Status selector
        ctk.CTkLabel(
            inner, text="// status",
            font=ctk.CTkFont(size=12),
            text_color=theme.MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 6))

        self._status_var = ctk.StringVar(value="consumed")
        radio_row = ctk.CTkFrame(inner, fg_color="transparent")
        radio_row.pack(fill="x", pady=(0, 14))
        for label, value in [
            ("Completed",    "consumed"),
            ("In Progress",  "consuming"),
            ("Plan to Read", "plan_to_consume"),
        ]:
            ctk.CTkRadioButton(
                radio_row, text=label,
                variable=self._status_var, value=value,
                text_color=theme.TEXT,
                fg_color=theme.ACCENT,
                border_color=theme.OVERLAY,
                font=ctk.CTkFont(size=13),
            ).pack(side="left", padx=(0, 22))

        ctk.CTkButton(
            inner, text="Add to Library",
            height=44, corner_radius=theme.R_MD,
            fg_color=theme.GREEN,
            hover_color="#7dc987",
            text_color=theme.BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._add_to_library,
        ).pack(anchor="w")

    def _add_to_library(self):
        print(f"[AddView] Add '{FAKE_RESULT['title']}' with status='{self._status_var.get()}'")
