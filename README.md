<p align="center">
  <img width="300" src="https://github.com/Egsagon/PHUB/blob/master/assets/logo.svg">
</p>

# PHUB - An API for Pornhub.
[![Downloads](https://static.pepy.tech/badge/phub)](https://pepy.tech/project/phub)
[![PyPI version](https://badge.fury.io/py/phub.svg)](https://badge.fury.io/py/phub)


PHUB is a hybrid API for Pornhub. It is able to communicate with Pornhub
using both web-scraping and Pornhub's HubTraffic API. It is
able to access most used or useful PH features, such as video searching,
accessing account features, video downloading, and a lot more.

> [!WARNING]
> This project is probably against Pornhub TOS. Use at your own risks.

## Installation

- Install using `pip` (python `3.11` or higher required, recommended version): 
```shell
pip install --upgrade phub
```

- Or from this repo to get the latest fixes/features:
```shell
pip install --upgrade git+https://github.com/EchterAlsFake/PHUB.git
```

- Or, for python 3.10 and higher. It Could also work for Python 3.6–9, but untested.
```shell
pip install --upgrade git+https://github.com/EchterAlsFake/PHUB.git@py-3.10
```

## Quickstart

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

# Note
<strong>This repository was initiated and maintained by [Egsagon](https://github.com/Egsagon)
He doesn't have any time to maintain this and transferred me the ownership.
I'll do my best to maintain this repository functional.</strong>


## License

PHUB uses GPLv3. See the `LICENSE` file.

## Contributing

Feel free to contribute to this project by submitting
feature requests, issues, bugs, or whatever.
