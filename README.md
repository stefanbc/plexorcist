
# Plexorcist

Plexorcist banishes your binge-watching ghosts and unclutters your Plex graveyard of watched videos!

In other words it's a small Python script that clears a specific Plex Media Server library of all watched videos.

**PSA: Run Plexorcist only on a Plex Media Server that you have access to and you're sure you want to clean a specific library. The author of this script is not liable for any unwanted data loss.**


## Features

- JSON config file
- Log file
    - Automatic creation and cleanup when file gets too big
    - Logs the timestamp for all actions
    - Logs the name of the series and episode title
    - Logs the space reclaimed after deletion
- IFTTT integration (via webhook)
- Series whitelist
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

See `contributing.md` for ways to get started.

Please adhere to this project's `code of conduct`.


## Authors

- [@stefanbc](https://www.github.com/stefanbc)


## License

[MIT](https://github.com/stefanbc/Plexorcist/blob/main/LICENSE)