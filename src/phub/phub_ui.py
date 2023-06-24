'''
Simple downloading UI script.
'''

try:
    import tkinter as tk
    from tkinter import ttk
    import tkinter.messagebox as tkmb
    import tkinter.filedialog as tkfd

except ModuleNotFoundError:
    print('Please install tkinter on your system before starting the UI.')
    exit()

import phub
from phub.utils import download_presets as dlp

import threading

class App(tk.Tk):
    
    def __init__(self, client: phub.Client) -> None:
        '''
        Represents an instance of the app.
        '''
        
        super().__init__()
        self.title('PHUB downloader')
        self.geometry('400x200')
        
        self.client = client
        
        # Widgets
        tk.Label(self, text = 'Enter video URL').pack()
        
        urlbox = tk.Frame(self)
        urlbox.pack(expand = True, fill = 'x', padx = 10)
        
        self.url = ttk.Entry(urlbox)
        self.url.bind('<Return>', self.run)
        self.url.pack(side = 'left', fill = 'x', expand = True)
        
        ttk.Button(urlbox, text = 'OK', command = self.run).pack(side = 'right')
        ttk.Button(urlbox, text = '...', command = self.params).pack(side = 'right')
        
        self.prog = ttk.Progressbar(self)
        self.prog.pack(fill = 'x', side = 'bottom', padx = 10, pady = 10)
        
        # Settings
        self.path = '.'
        self.quality = 'best'
    
    def params(self, *_) -> None:
        '''
        Open settings window.
        '''
        
        def save(*_) -> None:
            # Called on save
            
            self.quality = quality.get()
            self.path = pathvar.get()
            popup.destroy()
            
            print(self.quality, self.path)

        def fetch_path(*_) -> None:
            # Fetch path
            
            if path := tkfd.askdirectory(title = 'Select download directory'):
                pathvar.set(path)
        
        popup = tk.Toplevel(self)
        popup.title('Settings')
        
        tk.Label(popup, text = 'Settings').pack()
        ttk.Separator(popup).pack()
        
        tk.Label(popup, text = 'Video quality').pack()
        quality = tk.StringVar(popup, 'best')
        ttk.OptionMenu(popup, quality, 'best', 'best', 'middle', 'worst').pack()
        ttk.Separator(popup).pack()
        
        tk.Label(popup, text = 'Download path').pack()
        pathvar = tk.StringVar(self, '.')
        ttk.Button(popup, text = 'Open', command = fetch_path).pack()
        ttk.Separator(popup).pack()
        
        ttk.Button(popup, text = 'Save', command = save).pack()
        popup.mainloop()
    
    def updatebar(self, value: int) -> None:
        '''
        Update the progress bar.
        '''
        
        self.prog.config(value = value)
    
    def download(self, url) -> None:
        '''
        Download a video.
        '''
        
        try:
            path = self.client.get(url).download(
                path = self.path,
                quality = phub.Quality(self.quality),
                callback = dlp.percent(self.updatebar)
            )
            
            tkmb.showinfo('Success', 'Video downloaded: ' + path)
            self.prog.config(value = 0) # Reset progress bar
        
        except Exception as err:
            tkmb.showerror('Error', 'Something wrong happened:' + repr(err))
    
    def run(self, *_) -> None:
        '''
        Start the download.
        '''

        # Check if URL is right        
        url = self.url.get().strip()
        
        if not phub.consts.regexes.is_valid_video_url(url):
            return tkmb.showwarning('Error', 'Invalid video URL.')
        
        # Download
        threading.Thread(target = self.download, args = [url]).start()


def main(client) -> None:
    App(client).mainloop()

if __name__ == '__main__':
    main(phub.Client())

# EOF