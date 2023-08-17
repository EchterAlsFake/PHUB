![PHUB](https://github.com/Egsagon/PHUB/blob/master/assets/banner.png)

# PHUB - An API for PornHub.
PHUB is an API wrapper for PornHub. It is able to fetch, search and download videos and supports account connections, achieved with efficient web scrapping using requests and regexes.

> :warning: **Early development + not maintained a lot** don't hesitate to submit issues and PRs

## Installation
- Install using pip (python 3.11 or higher required):
```sh
pip install --upgrade phub
```

- Or using this repository to get latest features:
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

You can also use this beautiful UI made by EchterAlsFake: [EchterAlsFake/Porn_Fetch](https://github.com/EchterAlsFake/Porn_Fetch)

## Package usage
Example video download usage:
```python
import phub

client = phub.Client()
video = client.get('enter video URL here')

# Download on working dir with maximum quality
video.download('.', quality = phub.Quality.BEST)
```

Example searching for videos:
```python
query = client.search('enter query here')

# Display videos from 0 to 10
for video in query[:10]:
  print(video.title)
```

## Documentation
See [here](https://phub.readthedocs.io).

## Why?
This project was made as an enhancement for [pfetch](https://github.com/Egsagon/pornhub-fetch), which aimed at downloading videos from PornHub.
