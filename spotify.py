import os
import sys
import requests
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from pytube import YouTube, Search
import re
import threading
from PIL import Image, ImageTk

# Import custom themes
import TKinterModernThemes as TKMT
import sv_ttk

# Create a themed Tkinter frame for the app
class App(TKMT.ThemedTKinterFrame):
    def __init__(self):
        super().__init__("TKinter Custom Themes Demo")
        
        # Create a paned window for layout
        self.panedWindow = self.PanedWindow("Paned Window Test")
        self.pane1 = self.panedWindow.addWindow()

        # Create a notebook for tabbed interface
        self.notebook = self.pane1.Notebook("Notebook Test")
        self.tab1 = self.notebook.addTab("Tab Title")

# Class to handle YouTube downloading
class YouTubeDownloader:
    def __init__(self, query):
        self.query = query

    def sanitize_filename(self, filename):
        return re.sub(r'[\/:*?"<>|]', '', filename)

    def download_audio(self, progress_bar, progress_label, song_image_label):
        s = Search(self.query)
        video = s.results[0]
        url = video.watch_url
        yt_video = YouTube(url)
        sanitized_title = self.sanitize_filename(yt_video.title)

        try:
            # Download the audio stream
            stream = yt_video.streams.filter(only_audio=True).first()
            download_path = os.path.join("downloads", f"{sanitized_title}.mp3")
            stream.download(output_path="downloads", filename=f"{sanitized_title}.mp3")

            # Update UI after successful download
            progress_label.config(text="Download Successful!")
            progress_bar.stop()
            print('Download Successful')
            user_response = messagebox.askquestion("Download Completed", "Do you want to continue?")
            if user_response == 'yes':
                song_url_entry.delete(0, tk.END)
                song_info_label.config(text="")
                artist_info_label.config(text="")
                song_image_label.image = None
                progress_label.config(text="")
            elif user_response == 'no':
                window.destroy()
                sys.exit()
        except Exception as e:
            # Handle download failure
            print(e)
            progress_label.config(text="Download Failed")
            progress_bar.stop()
            print('Download Failed')

# Function to fetch song info and start download
def fetch_and_download():
    def download_thread():
        downloader = YouTubeDownloader(song_title)
        downloader.download_audio(progress_bar, progress_label, song_image_label)

    # Spotify API credentials
    CLIENT_ID = 'YOUR ID'
    CLIENT_SECRET = 'YOUR SECRET'
    
    # Get song URL and track ID from user input
    song_url = song_url_entry.get()
    track_id = song_url.split('/')[-1]
    
    # Authenticate with Spotify API
    auth_response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    auth_data = auth_response.json()
    access_token = auth_data['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Get track information from Spotify API
    response = requests.get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=headers)
    
    if response.status_code == 200:
        # Parse track data
        track_data = response.json()
        song_title = track_data['name']
        song_image = track_data['album']['images'][0]['url']
        song_artist = track_data['artists'][0]['name']
        
        # Update UI with song info
        song_info_label.config(text=f"Song Title: {song_title}")
        artist_info_label.config(text=f"Song Artist: {song_artist}")
        
        # Load and display song image
        img = Image.open(requests.get(song_image, stream=True).raw)
        img.thumbnail((200, 200))
        img = ImageTk.PhotoImage(img)
        song_image_label.config(image=img)
        song_image_label.image = img
        
        # Start downloading in a separate thread
        progress_label.config(text="Downloading...")
        progress_bar.start()
        threading.Thread(target=download_thread).start()
    else:
        messagebox.showerror("Error", "Failed to retrieve song information")

# Create the main GUI window
window = tk.Tk()
window.geometry("620x600")
window.title("Spotify Downloader")

# Set the theme
sv_ttk.set_theme("dark")

# Create and place ttk widgets
song_url_label = ttk.Label(window, text="Enter Spotify Song URL:")
song_url_label.pack(pady=10)

song_url_entry = ttk.Entry(window, width=50)
song_url_entry.pack(pady=10)

fetch_button = ttk.Button(window, text="Fetch Song and Download", command=fetch_and_download)
fetch_button.pack(pady=10)

song_info_label = ttk.Label(window, text="", font=("Helvetica", 12))
song_info_label.pack(pady=10)

artist_info_label = ttk.Label(window, text="", font=("Helvetica", 12))
artist_info_label.pack(pady=10)

# Display song image on the screen
song_image_label = Label(window)
song_image_label.pack(pady=10)

progress_label = ttk.Label(window, text="", font=("Helvetica", 12))
progress_label.pack(pady=10)

progress_bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()

# Button to exit the application
exit_button = ttk.Button(window, text="Exit", command=window.destroy)
exit_button.pack(pady=10)

# Start the GUI event loop
window.mainloop()
