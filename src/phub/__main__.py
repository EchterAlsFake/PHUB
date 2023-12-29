'''
PHUB built-in CLI.
'''

import phub

import os
import time
import click

@click.group()
def cli(): pass

@cli.command()
@click.argument('entry')
@click.option('--quality', '-q', help = 'Video quality', default = 'best')
@click.option('--output',  '-o', help = 'Output video file', default = '.')
@click.option('--pause',  '-p', help = 'Pause between downloads', default = 5)
@click.option('--threads',  '-t', help = 'Number of threads to use', default = 100)
def download(entry: str, quality: str, output: str, pause: str, threads) -> None:
    '''
    Download videos given a URL or a text file containing urls or keys.
    '''
    
    pause = int(pause)
    threads = int(threads)
    
    if entry.startswith('https://'):
            urls = [entry.strip()]
    
    else:
        with open(entry, 'r') as file:
            urls = file.read().split()
    
    client = phub.Client( delay = .1)
    length = len(urls)
    max_length = len(str(length))
    
    if length > 1 and os.path.isfile(output):
        print('\033[91mError\033[0m ~ Output is not a directory')
        exit()
    
    for index, url in enumerate(urls):
        try:
            video = client.get(url)
            
            video.download(path = output,
                           quality = quality,
                           downloader = phub.download.threaded(threads, 20),
                           display = phub.display.progress(
                               desc = f'{index: >{max_length}}/{length} ~ {video}',
                               color = dict(c1=37, c2=33, c3=36, c4=0)))
            
            time.sleep(pause)
            client.reset()
        
        except Exception as err:
            print(f'\033[91mError\033[0m ~ {repr(err)}')
    
    print('\n\033[33mProcess finished.\033[0m')

@cli.command()
@click.argument('entry')
@click.option('--max', '-m', help = 'Maximum number of videos', default = '40')
def search(entry: str, max: str) -> None:
    '''
    Search for videos.
    '''
    
    client = phub.Client()
    
    for video in client.search(entry).sample(int(max)):    
        print(f'{video.key} - {video.title}')

@cli.command()
def update_locals() -> None:
    '''
    Update PHUB locals that depend on PH.
    '''
    
    phub.utils.update_locals()

if __name__ == '__main__':
    cli()

# EOF