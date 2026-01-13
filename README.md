[![Pylint](https://github.com/stefanbc/plexorcist/actions/workflows/pylint.yml/badge.svg)](https://github.com/stefanbc/plexorcist/actions/workflows/pylint.yml) [![Tests](https://github.com/stefanbc/plexorcist/actions/workflows/testing.yml/badge.svg)](https://github.com/stefanbc/plexorcist/actions/workflows/testing.yml) [![CodeQL](https://github.com/stefanbc/plexorcist/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/stefanbc/plexorcist/actions/workflows/github-code-scanning/codeql) [![Maintainability](https://qlty.sh/gh/stefanbc/projects/plexorcist/maintainability.svg)](https://qlty.sh/gh/stefanbc/projects/plexorcist) [![Code Coverage](https://qlty.sh/gh/stefanbc/projects/plexorcist/coverage.svg)](https://qlty.sh/gh/stefanbc/projects/plexorcist) [![codecov](https://codecov.io/gh/stefanbc/plexorcist/branch/main/graph/badge.svg?token=V78UV6TNSM)](https://codecov.io/gh/stefanbc/plexorcist) [![Known Vulnerabilities](https://snyk.io/test/github/stefanbc/plexorcist/badge.svg)](https://snyk.io/test/github/stefanbc/plexorcist)

# Plexorcist

The Plexorcist banishes your binge-watching ghosts and unclutters your watched videos graveyard, bringing order and harmony to your Plex experience!

In other words it's a small Python script that cleans up any number of Plex Media Server libraries of all watched videos. Automatically delete watched episodes or movies, to clear up space on your Plex Media Server.

## Disclaimer

This script should only be executed on a Plex Media Server that you have authorized access to, and only if you are certain that you want to perform a clean-up on specific libraries. It is important to note that the author of this script cannot be held accountable for any unintended loss of data. It is advised that you exercise great caution and prudence before utilizing this script.

## Features

- Suppport for multiple libraries (Movies and TV Shows only)
- Movies and TV Shows whitelist
- Remove only videos older than
- Configurable via [config file](https://github.com/stefanbc/plexorcist/wiki/Configuration)
- I18N (via config file) - [feeling fancy?](https://github.com/stefanbc/plexorcist/wiki/I18N-King-James-Version)
- Logging
  - Automatic creation and cleanup when file gets too big (1 MB)
  - Logs the timestamp for all actions
  - Logs the name of the Movie or TV Show (including episode title)
  - Logs the space reclaimed after deletion
  - Requests error handling
- Pushbullet integration (via API key)
- IFTTT integration (via webhook)
- CSV report file (timestamp, number of deleted videos, GB reclaimed)

## Installation

### Recommended

Run this command in your terminal

```bash
wget -qO - https://raw.githubusercontent.com/stefanbc/plexorcist/main/plexorcist.sh | bash
```

### Manually

Clone Plexorcist

```bash
git clone https://github.com/stefanbc/plexorcist.git
```

Open Plexorcist

```bash
cd plexorcist
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

[Documentation](https://github.com/stefanbc/plexorcist/wiki)

## Contributing

Contributions are always welcome!

See [CONTRIBUTING.md](https://github.com/stefanbc/plexorcist/blob/main/CONTRIBUTING.md) for ways to get started.

Please adhere to this project's [code of conduct](https://github.com/stefanbc/plexorcist/blob/main/CODE_OF_CONDUCT.md).

## Contributors

[<img src="https://github.com/stefanbc.png" width="60px;"/><br /><sub><a href="https://github.com/stefanbc">stefanbc</a></sub>](https://github.com/stefanbc/plexorcist)

## License

[Apache License 2.0](https://github.com/stefanbc/plexorcist/blob/main/LICENSE)
