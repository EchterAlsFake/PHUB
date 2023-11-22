<p align="center">
  <img width="300" src="https://github.com/Egsagon/PHUB/blob/master/assets/logo.svg">
</p>

# PHUB - An API for Pornhub.

PHUB is an hybrid API for Pornhub. It is able to communicate with Pornhub
using both web-scraping and Pornhub's HubTraffic API. It is
able to access most used or useful PH features, such as video searching,
accessing account features, video downloading, and a lot more.

> [!WARNING]
> This project is probably against Pornhub TOS. Use at your own risks.

> [!CAUTION]
> The documentation for this project is a bit outdated. I don't have the time to do it, but if you are willing to help, PRs are welcome!

## Installation

- Install using `pip` (python `3.11` or higher required, recommended version): 
```shell
pip install --upgrade phub
```

- Or from this repo to get latest fixes/features:
```shell
pip install --upgrade git+https://github.com/Egsagon/PHUB.git
```

- Or, for python 3.9 and higher (:warning: not updated as often)
```shell
pip install --upgrade git+https://github.com/Egsagon/PHUB.git@py-3.9
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

## License

PHUB uses GPLv3. See the `LICENSE` file.

## Contributing

Feel free to contribute to this project by submiting
feature requests, issues, bugs, or whatever.
