
import customtkinter as ctk
import theme

def tag_pill(parent, text):
    frame = ctk.CTkFrame(parent, fg_color=theme.SURFACE1, corner_radius=theme.R_SM)
    frame.pack(side="left", padx=2, pady=2)
    ctk.CTkLabel(
        frame, text=text,
        fg_color="transparent",
        text_color=theme.SUBTEXT,
        font=ctk.CTkFont(size=12),
    ).pack(padx=9, pady=4)