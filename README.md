![PHUB](https://github.com/Egsagon/PHUB/blob/master/assets/banner.png)

# PHUB - An API for PornHub.
PHUB is an API wrapper for PornHub. It is able to fetch, search and download videos and supports account connections, achieved with efficient web scrapping using requests and regexes.

> ⚠️ This project is probably against Pornhub TOS.

## Installation
- Install using pip (python 3.11 or higher required):
```sh
pip install --upgrade phub
```

- Or using this repository to get the latest features:
```sh
pip install --upgrade git+https://github.com/Egsagon/PHUB.git
```

## CLI usage
You can use phub like so from the terminal as as CLI script:
```sh
python3 -m phub
```

Example for downloading a video knowing its url, in the best available quality:
```sh
python3 -m phub download --url https://www.pornhub.com/view_video.php?viewkey=xxx -q 'best'
```

## UI Usage
You can use this masterpiece made by EchterAlsFake: [EchterAlsFake/Porn_Fetch](https://github.com/EchterAlsFake/Porn_Fetch)

## Package usage
Exemple for downloading a video:
```python
import phub

client = phub.Client()
video = client.get('enter video URL here')
print('Downloading:', video.title)

# Download on working dir with best quality
video.download('.', quality = phub.Quality.BEST)
```

## Contributing

I don't plan to really maintain this after i start school, so feel free to support this project by submiting issues or requests
and share the bugs you encountered in [Known issues](https://github.com/Egsagon/PHUB/blob/master/KNOWN_ISSUES.md)

## Documentation
You can find out more on the API [in the docs](https://phub.readthedocs.io).

## License

GPLv3 - See the `LICENSE` file.
