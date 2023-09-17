'''
PHUB 4 CLI.
'''

import phub
import click

@click.group()
def cli(): pass

@cli.command()
@click.argument('url')
@click.option('--quality', '-q', help = 'Video quality', default = 'best')
@click.option('--output',  '-o', help = 'Output video file', default = '.')
def download(url, quality, output):
    '''
    Download a specific video.
    '''
    
    client = phub.Client()
    video = client.get(url)
    video.download(output, quality)

if __name__ == '__main__':
    cli()

# EOF