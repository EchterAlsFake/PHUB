<p align="center">
  <img src="https://github.com/Egsagon/PHUB/blob/master/assets/banner.png">
</p>

# PHUB - An API for PornHub.

PHUB is an API wrapper for Pornhub (PH).
It is able to communicate with most used PH
features such as video searching, downloading,
account connection, etc.

Learn more on the project [documentation](https://phub.readthedocs.io) and
[github page](https://github.com/Egsagon/PHUB).

## Installation

Dependencies: `requests`, `click`, `tqdm`

```sh
pip install -U phub
```

Or, development branch:
```sh
pip install -U git+https://github.com/Egsagon/PHUB.git`
```

## Exemple usage

```python
import phub

client = phub.Client()

video = client.get(url = '...')
video.download('my-video.mp4', quality = 'best')
```
