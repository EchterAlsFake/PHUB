# Example dowloading script

import phub

client = phub.Client()

def log(current: int, total: int) -> None:
    # Called to update downloading
    
    percent = round((current / total) * 100)
    print(f'\r[+] Downloading {current}/{total} ({percent}%)', end = '')

while 1:
    # Ask user for URL
    url = input('[*] Enter video URL: ').strip()
    
    if not phub.consts.regexes.is_valid_video_url(url):
        print('[-] Invalid video URL. Try again.')
        continue
    
    # Fetch video
    video = client.get(url = url)
    print(f'[+] Fetched video', video)
    
    # Ask user for quality
    quality = input('[*] Enter video quality (default=BEST): ') or 'BEST'
    quality = phub.Quality(quality)
    
    # Download the video
    video.download(path = '.', quality = quality,
                   quiet = True, callback = log)

    print('\nDone.')

# EOF