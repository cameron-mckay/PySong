import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter.messagebox import showinfo, showerror
from tkinter.constants import DISABLED, LEFT
from tkinter.filedialog import askopenfilenames, askdirectory
import os
from os import listdir
from os.path import isfile, join
from mutagen.easyid3 import EasyID3
from subprocess import call
from threading import Thread

class AudioGUI:
    # Initialize method
    # Builds the default UI with no files by default
    def __init__(self):
        # Build the main window
        self.__main_window = tk.Tk()
        self.__main_window.configure(background='white')
        self.__main_window.title('Pysong Library Manager')
        # Store all the audio files in a list
        self.__files = []
        self.__convert_list = []
        # File path blank by default
        self.__file_path = ''
        # Generate the GUI frames
        self.build_frames()
        tk.mainloop()

    def build_frames(self):
        # Build Frames
        self.__top_frame = tk.Frame(self.__main_window, bg='black')
        self.__grid = tk.Frame(self.__main_window)
        self.__bottom_frame = tk.Frame(self.__main_window)

        # Top frame
        self.__title = tk.Label(self.__top_frame, text='PySong Library Manager', bg='black', fg='white')
        self.__file_button = tk.Button(self.__top_frame, text='Choose Folder', command=self.select_folder)        
        self.__convert_button = tk.Button(self.__top_frame, text='Convert To MP3', command=self.convert)
        self.__file_label = tk.Label(self.__top_frame, text=self.__file_path, bg='black', fg='white')
        
        # Pack the top frame
        self.__title.pack(side='left')
        self.__file_button.pack(side='left')
        self.__convert_button.pack(side='left')
        self.__file_label.pack(side='left')
        self.__top_frame.pack(fill=tk.X, side='top')
        
        # Build the middle frame which also builds the bottom frame
        self.song_build()

# Rebuilds the song grid and bottom frame.  Usually whenever files are edited, or directory is changed.
    def song_build(self):
        self.__grid.destroy()
        self.__grid = tk.Frame(self.__main_window)
        
        # Build the header widgets
        self.__check_boxes_column = tk.Label(self.__grid, text='Select')
        self.__file_name_column = tk.Label(self.__grid, text='File Name')
        self.__title_column = tk.Label(self.__grid, text='Title')
        self.__artist_column = tk.Label(self.__grid, text='Artist')
        self.__album_column = tk.Label(self.__grid, text='Album')
        self.__genre_column = tk.Label(self.__grid, text='Genre')
        self.__year_column = tk.Label(self.__grid, text='Year')
        self.__number_column = tk.Label(self.__grid, text='Track Num')
        self.__format_column = tk.Label(self.__grid, text='Format')
        
        # Grid the header
        self.__check_boxes_column.grid(row=1, column=0)
        self.__file_name_column.grid(row=1, column=1)
        self.__title_column.grid(row=1, column=2)
        self.__artist_column.grid(row=1, column=3)
        self.__album_column.grid(row=1, column=4)
        self.__genre_column.grid(row=1, column=5)
        self.__year_column.grid(row=1, column=6)
        self.__number_column.grid(row=1, column=7)
        self.__format_column.grid(row=1, column=8)
        index = 1
        for audiofile in self.__files:
            index += 1
             # Updates info for songs and builds grids
            audiofile.build_row(self.__grid, index)
            # Repeat for all songs
        # Pack the grid to fill the window
        self.__grid.pack(fill=tk.X)
        self.build_bottom_frame()
        if len(self.__files) == 0:
            self.__edit_button.config(state=DISABLED)
    # Builds the bottom frame in default view
    def build_bottom_frame(self):
        self.__bottom_frame.destroy()
        self.__bottom_frame = tk.Frame(self.__main_window)
        self.__edit_button = tk.Button(self.__bottom_frame, text='Edit', command=self.edit)
        self.__edit_button.pack(side='left')
        self.__bottom_frame.pack(fill=tk.X)
        
    # Gets a file directory from the user
    def select_folder(self):
        # Choose folder code
        self.__files.clear()
        self.__file_path = askdirectory()
        if self.__file_path != '':
            for f in listdir(self.__file_path):
                if isfile(join(self.__file_path, f)):
                    if f.endswith('.mp3'):
                        self.__files.append(AudioFile(self.__file_path+'/'+f, f))
        self.rebuild_all()

    # Rebuilds all frames in the default view
    def rebuild_all(self):
        self.__top_frame.destroy()
        self.__grid.destroy()
        self.__bottom_frame.destroy()
        self.build_frames()

    def convert(self):
        self.__files.clear()
        self.__file_path = ''
        self.rebuild_all()
        # Choose files to convert to mp3
        self.__convert_list = askopenfilenames(filetypes=[("Audio Files", "*.flac *.wav *.ogg")])
        if len(self.__convert_list) != 0:
            # Create progress bar
            self.__progress_label = tk.Label(self.__bottom_frame, text='Progress: ')
            self.__progress = Progressbar(self.__bottom_frame, orient="horizontal", length=100, mode='determinate')
            self.__progress_label.pack(side='left')
            self.__progress.pack(side='left')
            self.__convert_button.config(state=DISABLED)
            self.__edit_button.config(state=DISABLED)
            self.__file_button.config(state=DISABLED)
            # Creates new thread for FFMPEG conversion
            conv_thread = Thread(target=self.conver)
            conv_thread.start()        
    def conver(self):
        self.__progress['value'] = 0
        percent = 100/len(self.__convert_list)
        # Convert all files using ffmpeg
        try:
            for audiofile in self.__convert_list:
                self.__main_window.update()
                try:
                    if audiofile.endswith('.flac'):
                        call(['ffmpeg.exe', '-i', audiofile, audiofile[0:-4]+'mp3', '-y'])
                    else:
                        call(['ffmpeg.exe', '-i', audiofile, audiofile[0:-3]+'mp3', '-y'])
                except:
                    if audiofile.endswith('.flac'):
                        call(['ffmpeg', '-i', audiofile, audiofile[0:-4]+'mp3', '-y'])
                    else:
                        call(['ffmpeg', '-i', audiofile, audiofile[0:-3]+'mp3', '-y'])
            tk.messagebox.showinfo('Success', 'Successfully converted '+str(len(self.__convert_list))+' files.')
        except:
            tk.messagebox.showerror('ERROR', 'FFMPEG required for file conversion.')
            self.__progress['value'] += percent
        self.__progress.destroy()
        self.__progress_label.destroy()
        self.rebuild_all()

    def edit(self):
        index = -1
        row = 1
        # Check if any files are selected
        for audiofile in self.__files:
            row += 1
            if audiofile.edit(self.__grid, row) == 1:
                index += 1
        # If files are selected, disable buttons
        if index != -1:    
            self.__save_button = tk.Button(self.__bottom_frame, text='Save', command=self.save)
            self.__convert_button.config(state=DISABLED)
            self.__edit_button.config(state=DISABLED)
            self.__save_button.pack(side='left')
            self.__file_button.config(state=DISABLED)
            for audiofile in self.__files:
                audiofile.disable_check()
        # If not the function ends and nothing changes for the user

    def save(self):
        # Same indexing as the edit function
        # Set all the audio file object values to the edited values
        for audiofile in self.__files:
            audiofile.save()
        # Rebuild the UI in the default mode
        self.rebuild_all()

class AudioFile:
    
    def __init__(self, path, file_name):
        # Initialize ID3 handle and key values
        self.__path = path
        self.__file_name = file_name
        self.__id3 = EasyID3(self.__path)
        self.__id3.RegisterTextKey('artist', 'TPE2')
        self.__id3.RegisterTextKey('year', 'TDAT')
        self.__id3.RegisterTextKey('album', 'TALB')
        self.__id3.RegisterTextKey('genre', 'TCON')
        self.__id3.RegisterTextKey('number', 'TRCK')

        # String vars for labels and entry boxes
        self.__title_stringvar = tk.StringVar()
        self.__artist_stringvar = tk.StringVar()
        self.__album_stringvar = tk.StringVar()
        self.__genre_stringvar = tk.StringVar()
        self.__year_stringvar = tk.StringVar()
        self.__number_stringvar = tk.StringVar()
        self.__int_var = tk.IntVar()
        self.__format = tk.StringVar()
        self.update_stringvar()

    def build_row(self, frame, row):
        self.update_stringvar()
        # Build check boxes and labels
        self.__check_box = tk.Checkbutton(frame, variable=self.__int_var, onvalue=1, offvalue=0)
        self.__file_name_label = tk.Label(frame, text=self.__file_name)
        self.__title_label = tk.Label(frame, textvariable=self.__title_stringvar)
        self.__artist_label = tk.Label(frame, textvariable=self.__artist_stringvar)
        self.__album_label = tk.Label(frame, textvariable=self.__album_stringvar)
        self.__genre_label = tk.Label(frame, textvariable=self.__genre_stringvar)
        self.__year_label = tk.Label(frame, textvariable=self.__year_stringvar)
        self.__number_label = tk.Label(frame, textvariable=self.__number_stringvar)
        self.__format_label = tk.Label(frame, textvariable=self.__format)

        # Grid the objects    
        self.__grid(row)
    def __grid(self, row):
        self.__check_box.grid(column=0, row=row)
        self.__file_name_label.grid(column=1, row=row)
        self.__title_label.grid(column=2, row=row)
        self.__artist_label.grid(column=3, row=row)
        self.__album_label.grid(column=4, row=row)
        self.__genre_label.grid(column=5, row=row)
        self.__year_label.grid(column=6, row=row)
        self.__number_label.grid(column=7, row=row)
        self.__format_label.grid(column=8, row=row)
    def is_selected(self):
        if self.__int_var.get() == 1:
            return True
        else:
            return False
    def get_path(self):
        return self.__path
    def edit(self, frame, row):
        self.__check_box.destroy()
        self.__title_label.destroy()
        self.__artist_label.destroy()
        self.__album_label.destroy()
        self.__genre_label.destroy()
        self.__year_label.destroy()
        self.__number_label.destroy()
        self.__format_label.destroy()

        # If the checkbox is selected
        if self.__int_var.get() == 1:
            self.__check_box = tk.Checkbutton(frame, variable=self.__int_var, onvalue=1, offvalue=0)
            self.__title_label = tk.Entry(frame, textvariable=self.__title_stringvar)
            self.__artist_label = tk.Entry(frame, textvariable=self.__artist_stringvar)
            self.__album_label = tk.Entry(frame, textvariable=self.__album_stringvar)
            self.__genre_label = tk.Entry(frame, textvariable=self.__genre_stringvar)
            self.__year_label = tk.Entry(frame, textvariable=self.__year_stringvar)
            self.__number_label = tk.Entry(frame, textvariable=self.__number_stringvar)
            self.__format_label = tk.Label(frame, textvariable=self.__format)
            self.__grid(row)
            return 1
        else:
            # If checkbox is not selected
            self.build_row(frame, row)
            return 0

    def disable_check(self):
        self.__check_box.config(state=DISABLED)

    def update_stringvar(self):
        # Update stringvars with data from the ID3 files
        try:
            self.__title_stringvar.set(self.__id3['title'][0])
        except:
            self.__title_stringvar.set('')
        try:
            self.__artist_stringvar.set(self.__id3['artist'][0])
        except:
            self.__artist_stringvar.set('')
        try:
            self.__album_stringvar.set(self.__id3['album'][0])
        except:
            self.__album_stringvar.set('')
        try:
            self.__genre_stringvar.set(self.__id3['genre'][0])
        except:
            self.__genre_stringvar.set('')
        try:
            self.__year_stringvar.set(self.__id3['date'][0])
        except:
            self.__year_stringvar.set('')
        try:
            self.__number_stringvar.set(self.__id3['number'][0])
        except:
            self.__number_stringvar.set('')    
        if self.__path.endswith('.mp3'):
            self.__format.set('mp3')
        else:
            self.__format.set('wav')

    def save(self):
        # Save the data in textboxes to id3 files
        if self.__int_var.get() == 1:
            try:
                self.__id3['title'] = self.__title_stringvar.get()
            except:
                print('cannot change title')
            try:
                self.__id3['artist'] = self.__artist_stringvar.get()
            except:
                print('cannot change artist')
            try:
                self.__id3['album'] = self.__album_stringvar.get()
            except:
                print('cannot change album')
            try:
                self.__id3['genre'] = self.__genre_stringvar.get()
            except:
                print('cannot change genre')
            try:
                self.__id3['date'] = self.__year_stringvar.get()
            except:
                print('cannot change year')
            try:
                self.__id3['number'] = self.__number_stringvar.get()
            except:
                print('cannot change number').get()
            self.__id3.save()
        self.update_stringvar()

audio_ = AudioGUI()