# Example dowloading script

import phub

client = phub.Client()

url = input('Enter video url > ')
quality = input('Enter quality (default=best) > ') or 'best'

video = client.get(url)
path = video.download('.', quality)

print(f'Video as been downloaded as: `{path}`.')