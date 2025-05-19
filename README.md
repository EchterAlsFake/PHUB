<p align="center">
  <img width="200" src="https://github.com/Egsagon/PHUB/blob/master/assets/logo.svg">
</p>

<div align="center">
    <a href="https://pepy.tech/project/phub"><img src="https://static.pepy.tech/badge/phub" alt="Downloads"></a>
    <a href="https://badge.fury.io/py/phub"><img src="https://badge.fury.io/py/phub.svg" alt="PyPI version" height="18"></a>
    <a href="https://github.com/EchterAlsFake/PHUB/workflows/"><img src="https://github.com/EchterAlsFake/PHUB/actions/workflows/tests.yml/badge.svg" alt="API Tests"/></a>
</div>

<br>
PHUB is an easy-to-use API wrapper for Pornhub. It can access most used or useful
PH features, such as video searching, account features, video downloading, and more.

> [!WARNING]
> This project is probably against Pornhub TOS. Use at your own risks.

# Installation

- Install using `pip` (python `3.9` or higher required): 
```shell
pip install --upgrade phub
```

- Or from this repo to get the latest fixes/features:
```shell
pip install --upgrade git+https://github.com/EchterAlsFake/PHUB.git
```

# Usage from command line
```shell
# Download a single video
py -m phub https://www.pornhub.com/view_video.php?viewkey=abcdef
# Download multiple videos from a text file
py -m phub path/to/file.txt --quality best --downloader threaded --output video.mp4
```

# Quickstart

> [!NOTE]
> You can find the docs on this project [here](https://phub.readthedocs.io).

```python
import phub
from phub.locals import *

# Initialise a client
client = phub.Client()

# Fetch and download a video
video = client.get('https://...')
video.download('my-video.mp4', Quality.BEST)

# Fetch user videos
user = client.get_user('this-user')
for video in user.videos:
    print(video.title)

# Perform a research
for video in client.search('my-query'):
    print(video.title)

# Connect to an account
client = phub.Client('my-username', 'my-password')

# Access account history, liked and recommended stuff
client.account.watched
client.account.liked
client.account.recommended
```

# License
PHUB uses GPLv3. See the `LICENSE` file.

This repository was initiated and maintained by [Egsagon](https://github.com/Egsagon)
He doesn't have any time to maintain this and transferred me the ownership.
I'll do my best to maintain this repository functional.

# Contributing
Feel free to contribute to this project by submitting
feature requests, issues, bugs, or whatever.
