'''
PHUB CLI script.
'''

import phub
import click

from phub.utils import download_presets as dlp

@click.group()
def cli() -> None:
    pass

@cli.command()
def ui():
    '''
    Run in UI mode.
    '''
    
    from phub import phub_ui
    phub_ui.main()

@cli.command()
@click.option('--url',     '-u', help = 'Video URL')
@click.option('--quality', '-q', help = 'Video quality', default = 'best')
@click.option('--output',  '-o', help = 'Output video file', default = '.')
def download(url, quality, output):
    '''
    Download a specific video.
    '''
    
    # Initialise client
    client = phub.Client()
    
    # Fetch the video
    try:
        video = client.get(url)
    
    except Exception as err:
        return click.secho(f'[ERR] Could not fetch video: {err}', fg = 'red')
    
    # Download video
    try:
        path = video.download(path = output, quality = phub.Quality(quality),
                              callback = dlp.bar(desc = 'Downloading ' + video.key))
    
    except Exception as err:
        return click.secho(f'[ERR] Could not download video: {err}', fg = 'red')
    
    click.secho('Downloaded video at:\n\t' + path, fg = 'green')

if __name__ == '__main__':
    
    cli()


# EOF