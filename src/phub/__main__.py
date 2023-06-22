'''
Main PHUB script.
'''

import phub
import click

@click.command()
@click.option('--url',       '-u', help = 'URL of the video.')
@click.option('--key',       '-k', help = 'Viewkey of the video.')
@click.option('--quality',   '-q', help = 'Video quality (default=best)', default = 'best')
@click.option('--output',    '-o', help = 'File output', default = '.')
@click.option('--noconfirm', '-n', help = 'Prevent confirming things.')

def main(url: str, key: str, quality: str, output: str, noconfirm: str) -> None:
    '''
    Main script.
    '''
    
    if not any((url, key)):
        return click.secho('Error: Specify either --url or --key', fg = 'red', err = 1)
    
    client = phub.Client()
    video = client.get(url, key)
    
    if not bool(noconfirm):
        if not click.confirm('Download ' + click.style(video, fg = 'green'), default = 1):
            return click.secho('Download aborted', fg = 'red', err = 1)
    
    # Display downloading process.
    def log(cur: int, total: int) -> None:   
        click.echo(f'\rDownloading: {round((cur / total) * 100)}%', nl = 0)
    
    # Download
    try:
        path = video.download(path = output, quality = phub.Quality(quality),
                              callback = log, quiet = True)
    
    except Exception as err:
        return click.secho(f'Error: {type(err)} {err}', fg = 'red', err = 1)
    
    return click.echo('\rDownloaded video at ' + click.style(path, fg = 'green'))


if __name__ == '__main__':
    main()

# EOF