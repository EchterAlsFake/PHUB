'''
PHUB built-in CLI.
'''
import os
import phub

try:
    import click

except (ModuleNotFoundError, ImportError):
    print("The CLI needs 'click' in order to work. Please do: 'pip install click'")
    exit()


@click.command()
@click.argument('input')
@click.option('--output', help = 'Output file or directory', default = './')
@click.option('--quality', help = 'Video quality', default = 'best')
@click.option('--downloader', help = 'Video downloader (default, FFMPEG or threaded)', default = 'FFMPEG')
def main(input: str, output: str, quality: str, downloader: str) -> None:
    
    downloader = getattr(phub.download, downloader.strip())
    
    if os.path.isfile(input):
        with open(input, encoding = 'utf-8') as file:
            urls = phub.consts.re.get_urls(file.read())

    else:
        urls = [input]
        
    if len(urls) > 1 and os.path.isfile(output):
        raise Exception('Must specify directory when downloading multiple videos.')
    
    client = phub.Client(delay = .02)
    
    for url in urls:
        try:
            video = client.get(url.strip())
            video.download(
                path = output,
                quality = quality,
                downloader = downloader,
                display = phub.display.bar(f'Downloading {video.key}')
            )
        
        except Exception as err:
            print(f'\x1b[91mError: {err}\x1b[0m')

if __name__ == '__main__':
    main()

# EOF