import customtkinter as ctk
from app.downloader_app import YouTubeDownloaderApp

ctk.set_appearance_mode("dark")  # "system" (default), "light", "dark"
ctk.set_default_color_theme("blue") # "blue" (standard), "dark-blue" and "green"

if __name__ == '__main__':
    root = ctk.CTk()
    app  = YouTubeDownloaderApp(root)
    root.mainloop()

