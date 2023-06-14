![PHUB](https://github.com/Egsagon/PHUB/blob/master/assets/banner.png)

# PHUB - An API for PornHub.
PHUB is an API wrapper for PornHub. It is able to fetch, search and download videos and supports account connections, achieved with efficient web scrapping using requests and regexes.

> :warning: **Early development: bugs may occur** (also i'm a terrible programer)

## Installation
- Install using pip:
```sh
pip install --upgrade phub
```

- Or using this repository to get latest features:
```sh
pip install --upgrade git+https://github.com/Egsagon/PHUB.git
```

## Usage
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
record = client.search('enter query here')

# Display all videos (careful if there is a lot of results)
for video in record:
  print(video.title)
```

## Documentation
See the [wiki](https://github.com/Egsagon/PHUB/wiki).

## Why?
This project was made as an enhancement for [pfetch](https://github.com/Egsagon/pornhub-fetch), which aimed at downloading videos from PornHub.
