
# Plexorcist

The Plexorcist banishes your binge-watching ghosts and unclutters your watched videos graveyard, bringing order and harmony to your Plex experience!

In other words it's a small Python script that clears a specific Plex Media Server library of all watched videos.

**PSA: Run Plexorcist only on a Plex Media Server to which you have access and are certain you want to clean a specific library. The creator of this script is not responsible for any unintended data loss.**


## Features

- Suppport for Movies or TV Shows
- JSON config file
- I18N (via config file) - [feeling fancy?](https://github.com/stefanbc/Plexorcist/wiki/I18N---King-James-Version)
- Log file
    - Automatic creation and cleanup when file gets too big (2 MB)
    - Logs the timestamp for all actions
    - Logs the name of the Movie or TV Show (including episode title)
    - Logs the space reclaimed after deletion
- IFTTT integration (via webhook)
- Movies or TV Shows whitelist
- Dry run the script and output the result in console
- Requests error handling


## Installation

Clone Plexorcist

```bash
  git clone https://github.com/stefanbc/Plexorcist.git
```

Open Plexorcist

```bash
  cd Plexorcist
```

Install the dependencies

```bash
  pip install -r requirements.txt
```

Give permissions to Plexorcist

```bash
  chmod +x plexorcist.py
```

Before running Plexorcist for the first time please read the [Documentation](#documentation).


## Documentation

[Documentation](https://github.com/stefanbc/Plexorcist/wiki)


## Contributing

Contributions are always welcome!

See [CONTRIBUTING.md](https://github.com/stefanbc/Plexorcist/blob/main/CONTRIBUTING.md) for ways to get started.

Please adhere to this project's [code of conduct](https://github.com/stefanbc/Plexorcist/blob/main/CODE_OF_CONDUCT.md).


## Authors

- [@stefanbc](https://www.github.com/stefanbc)


## License

[MIT](https://github.com/stefanbc/Plexorcist/blob/main/LICENSE)
