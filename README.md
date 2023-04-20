
# Plexorcist

Plexorcist banishes your binge-watching ghosts and unclutters your Plex graveyard of watched videos!

In other words it's a small Python script that clears a specific Plex Media Server library of all watched videos.

**PSA: Run Plexorcist only on a Plex Media Server to which you have access and are certain you want to clean a specific library. The creator of this script is not responsible for any unintended data loss.**


## Features

- Suppport for Movies and TV Shows
- JSON config file
- Log file
    - Automatic creation and cleanup when file gets too big
    - Logs the timestamp for all actions
    - Logs the name of the Movie or TV Show (including episode title)
    - Logs the space reclaimed after deletion
- IFTTT integration (via webhook)
- Movies and / or TV Shows whitelist
- Dry run the script and output the result via argument


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

Before running Plexorcist for the first time please read the [Documentation](#documentation)

Dry-run Plexorcist

```bash
  ./plexorcist.py --cast
```


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