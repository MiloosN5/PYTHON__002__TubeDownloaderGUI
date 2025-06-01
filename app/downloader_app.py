import customtkinter as ctk
from tkinter import messagebox
from pytubefix import YouTube

import threading
import os
import subprocess
import platform

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.url_var = ctk.StringVar() # URL of the video in the form of string

        # Wrapping everything inside a frame
        main_frame = ctk.CTkFrame(root, fg_color='#313535')
        main_frame.grid(row=0, column=0, padx=20, pady=20)        

        for i in range(6):
            main_frame.grid_rowconfigure(i, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)

        # 1. Label for URL input

        self.youtube_label = ctk.CTkLabel(main_frame, text="YouTube URL:", font=ctk.CTkFont(size=22), text_color="white")
        self.youtube_label.grid(row=0, column=0, pady=(20, 0))

        # 2. Entry (input) + Button

        entry_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        entry_button_frame.grid(row=1, column=0, pady=10, padx=20)

        entry_button_frame.grid_columnconfigure(0, weight=1)
        entry_button_frame.grid_columnconfigure(1, weight=1)

        self.entry = ctk.CTkEntry(entry_button_frame, textvariable=self.url_var, fg_color="white", text_color='#000', width=200)
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="e")

        self.download_button = ctk.CTkButton(entry_button_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=0, column=1, sticky="w")

        # 3. Progress bar

        self.progress = ctk.CTkProgressBar(main_frame)
        self.progress.set(0)
        self.progress.grid(row=2, column=0, padx=20, sticky="ew")

        # 4. Progress bar Label

        self.progress_label = ctk.CTkLabel(main_frame, text="Progress: 0%", font=ctk.CTkFont(size=12))
        self.progress_label.grid(row=3, column=0, pady=(5, 0))

        # 5. Play button

        self.play_button = ctk.CTkButton(main_frame, text='Play', state='disabled', command=self.play_video)
        self.play_button.grid(row=4, column=0, pady=20)

        self.video_path = None

        # prati širinu prozora
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        total_width = self.root.winfo_width()
        if total_width < 420:
            self.entry.grid_configure(row=0, column=0,  padx=0, pady=(0, 5), sticky="ew")
            self.download_button.grid_configure(row=1, column=0, sticky="ew")
            self.play_button.grid_configure(row=4, column=0, padx=20, sticky="ew")
        else:
            self.entry.grid_configure(row=0, column=0, padx=(0, 10), pady=0, sticky="e")
            self.download_button.grid_configure(row=0, column=1, sticky="w")   
            self.play_button.grid_configure(row=4, column=0, sticky="")     

    def start_download(self):
        self.download_button.configure(state='disabled')
        thread = threading.Thread(target=self.download_video)
        thread.start()

    def download_video(self):
        try:
            url = self.url_var.get().strip()
            if not url:
                raise Exception("Please enter a YouTube URL.")
            
            yt = YouTube(url, on_progress_callback=self.update_progress)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            self.video_path = stream.download(filename='youtube_video.mp4')
            
            self.root.after(0, lambda: self.progress.set(1.0))  # 100%
            self.root.after(0, lambda: self.progress_label.configure(text="Progress: 100%"))
            self.root.after(0, lambda: self.download_button.configure(text='Downloaded'))
            self.root.after(0, lambda: self.play_button.configure(state='normal'))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Video downloaded successfully!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
            self.root.after(0, lambda: self.download_button.configure(state='normal', text='Try again?'))
        finally:
            self.root.after(0, lambda: self.download_button.configure(border_color='white', border_width=1))
    
    def update_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        downloaded = total_size - bytes_remaining
        percent = downloaded / total_size
        
        self.root.after(0, lambda: self.progress.set(percent))
        self.root.after(0, lambda: self.progress_label.configure(text=f"Progress: {int(percent * 100)}%"))

    def play_video(self):
        if not self.video_path or not os.path.exists(self.video_path):
            messagebox.showerror("Error", "Downloaded video not found.")
            return

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(self.video_path)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", self.video_path])
            else:  # Linux
                subprocess.call(["xdg-open", self.video_path])

        except Exception as e:
            messagebox.showerror("Error", f"Could not open video: {str(e)}")