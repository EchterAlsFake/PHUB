'''
PHUB 4 CLI.
'''

import phub
import click

@click.group()
def cli(): pass

@cli.command()
@click.argument('entry')
@click.option('--quality', '-q', help = 'Video quality', default = 'best')
@click.option('--output',  '-o', help = 'Output video file', default = '.')
def download(entry: str, quality: str, output: str) -> None:
    '''
    Download a specific video.
    '''
    
    client = phub.Client()
    
    urls = [entry]
    if entry.endswith('.txt'):
        with open(entry, 'r') as file:
            urls = file.read().split()
    
    for url in urls:
        video = client.get(url)
        print(f'Downloading video \033[92m{video.key}\033[0m')
        video.download(output, quality)

@cli.command()
@click.argument('query')
def search(query: str) -> None:
    pass # TODO

if __name__ == '__main__':
    cli()

# EOF