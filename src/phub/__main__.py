'''
PHUB CLI script.
'''

import phub
import click

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
    Donload videos from Pornhub.
    '''
    
    client = phub.Client()
    
    try:
        video = client.get(url)
    
    except Exception as err:
        return click.secho(f'[ERR] Could not fetch video: {err}', fg = 'red')
    
    try:
        path = video.download(path = output,
                              quality = phub.Quality(quality))
    
    except Exception as err:
        return click.secho(f'[ERR] Could not download video: {err}', fg = 'red')
    
    click.secho('Downloaded video at:\n\t' + path, fg = 'green')

if __name__ == '__main__':
    
    cli()


# EOF