import customtkinter as ctk

def onclick():
    print("clicked")

app = ctk.CTk()
app.title("Test")


label = ctk.CTkLabel(app, text="Hello")
label.pack(pady=20)

button = ctk.CTkButton(app, text="Click me", command=onclick)
button.pack(pady=10)

app.mainloop()