# AddView; search and add manga/anime manually
import customtkinter as ctk
import theme
from api import extract_tags
from utils import tag_pill






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

        query = self._search_entry.get().strip()
        if not query:
            return

        media_type = self._type_seg.get().lower()  # "Manga" → "manga"

        result = self.app.client.search_media(media_type, query)
        if result is None:
            ctk.CTkLabel(
                self._result_frame, text="No results found.",
                text_color=theme.MUTED, font=ctk.CTkFont(size=14),
            ).pack(pady=20)
            return

        # Extract what we need
        self._current_result = {
            "mal_id": result["mal_id"],
            "media_type": media_type,
            "title": result["title"],
            "cover_url": result["images"]["jpg"]["large_image_url"],
            "synopsis": result.get("synopsis"),
            "tags": extract_tags(result),
            "mal_score": result.get("score"),
        }
        self._show_result()

    def _show_result(self):
        r = self._current_result

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
            inner, text=r["title"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.TEXT, anchor="w",
        ).pack(fill="x")

        score_text = f"MAL Score  {r['mal_score']}" if r["mal_score"] else "MAL Score  Unrated"
        ctk.CTkLabel(
            inner, text=score_text,
            font=ctk.CTkFont(size=14),
            text_color=theme.ACCENT, anchor="w",
        ).pack(fill="x", pady=(3, 10))

        tags_row = ctk.CTkFrame(inner, fg_color="transparent")
        tags_row.pack(fill="x", pady=(0, 10))
        for tag in r["tags"]:
            tag_pill(tags_row, tag)

        synopsis_box = ctk.CTkTextbox(
            inner, height=80,
            fg_color=theme.MANTLE,
            text_color=theme.SUBTEXT,
            border_color=theme.OVERLAY, border_width=1,
            corner_radius=theme.R_MD,
            font=ctk.CTkFont(size=13), wrap="word",
        )
        synopsis_box.insert("1.0", r["synopsis"] or "No description available.")
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
        radio_row.pack(fill="x", pady=(0, 8))
        for label, value in [
            ("Completed", "consumed"),
            ("In Progress", "consuming"),
            ("Plan to Read", "plan_to_consume"),
        ]:
            ctk.CTkRadioButton(
                radio_row, text=label,
                variable=self._status_var, value=value,
                text_color=theme.TEXT,
                fg_color=theme.ACCENT,
                border_color=theme.OVERLAY,
                font=ctk.CTkFont(size=13),
                command=self._on_status_change,
            ).pack(side="left", padx=(0, 22))

        # Liked row — only visible when Completed is selected
        self._liked_var = ctk.StringVar(value="1")
        self._liked_row = ctk.CTkFrame(inner, fg_color="transparent")
        # pack it now — _on_status_change will hide it if needed
        self._liked_row.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            self._liked_row, text="Did you like it?",
            font=ctk.CTkFont(size=13),
            text_color=theme.SUBTEXT,
        ).pack(side="left", padx=(0, 16))
        for label, value in [("Liked", "1"), ("Disliked", "0")]:
            ctk.CTkRadioButton(
                self._liked_row, text=label,
                variable=self._liked_var, value=value,
                text_color=theme.TEXT,
                fg_color=theme.GREEN if value == "1" else theme.RED,
                border_color=theme.OVERLAY,
                font=ctk.CTkFont(size=13),
            ).pack(side="left", padx=(0, 16))

        self._action_btn = ctk.CTkButton(
            inner, text="Add to Library",
            height=44, corner_radius=theme.R_MD,
            fg_color=theme.GREEN, hover_color="#7dc987",
            text_color=theme.BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._add_to_library,
        )
        self._action_btn.pack(anchor="w")

    def _on_status_change(self):
        if self._status_var.get() == "consumed":
            self._liked_row.pack(fill="x", pady=(0, 12))
        else:
            self._liked_row.pack_forget()

    def _add_to_library(self):
        r = self._current_result
        status = self._status_var.get()
        liked = int(self._liked_var.get()) if status == "consumed" else None

        self.app.db.add_media(
            mal_id=r["mal_id"],
            media_type=r["media_type"],
            title=r["title"],
            status=status,
            tags=r["tags"],
            liked=liked,
        )
        self._added = True
        self._action_btn.configure(
            text="✓ Added — Remove from Library",
            fg_color="transparent",
            border_width=1,
            border_color=theme.RED,
            text_color=theme.RED,
            hover_color="#3d1f25",
            command=self._remove_from_library,
        )
        print(f"[AddView] Added '{r['title']}' status={status} liked={liked}")

    def _remove_from_library(self):
            r = self._current_result
            self.app.db.delete_media(r["mal_id"], r["media_type"])
            # reset button back
            self._action_btn.configure(
                text="Add to Library",
                fg_color=theme.GREEN,
                hover_color="#7dc987",
                text_color=theme.BG,
                border_width=0,
                command=self._add_to_library,
            )
