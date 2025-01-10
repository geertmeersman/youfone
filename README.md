<img src="https://github.com/geertmeersman/youfone/raw/main/images/brand/logo.png"
     alt="Youfone"
     align="right"
     style="width: 200px;margin-right: 10px;" />

# Youfone for Home Assistant

A Home Assistant integration allowing to monitor your Youfone usage

```text
In order to avoid IP blacklisting / DDOS identification, the update interval is set to a minimum of 2 hours (you can increase it in the configuration).
When Home Assistant restarts, it will fetch the data from the local storage and it will update the sensors after the configured interval.
When adding a hub of the integration, it might take 1 minute to complete the addition, due to a 5 seconds interval set between each API call to Youfone.
```

### Features

- 📱 Mobile data sensors
- 📞 Voice & sms sensors
- 💲 Youcoins balance
- 📈 Invoice sensors
- 👱 User account information

---

<!-- [START BADGES] -->
<!-- Please keep comment here to allow auto update -->

[![maintainer](https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github)](https://github.com/geertmeersman)
[![buyme_coffee](https://img.shields.io/badge/Buy%20me%20an%20Omer-donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/geertmeersman)
[![discord](https://img.shields.io/discord/1094977038269546576?style=for-the-badge&logo=discord)](https://discord.gg/JpjHptEN2D)

[![discord](http://invidget.switchblade.xyz/JpjHptEN2D)](https://discord.gg/JpjHptEN2D)

[![MIT License](https://img.shields.io/github/license/geertmeersman/youfone?style=flat-square)](https://github.com/geertmeersman/youfone/blob/master/LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)

[![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=geertmeersman&repository=youfone&category=integration)

[![GitHub issues](https://img.shields.io/github/issues/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/issues)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/geertmeersman/youfone.svg)](http://isitmaintained.com/project/geertmeersman/youfone)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/geertmeersman/youfone.svg)](http://isitmaintained.com/project/geertmeersman/youfone)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/geertmeersman/youfone/pulls)

[![Hacs and Hassfest validation](https://github.com/geertmeersman/youfone/actions/workflows/validate.yml/badge.svg)](https://github.com/geertmeersman/youfone/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://github.com/geertmeersman/youfone/search?l=python)

[![manifest version](https://img.shields.io/github/manifest-json/v/geertmeersman/youfone/master?filename=custom_components%2Fyoufone%2Fmanifest.json)](https://github.com/geertmeersman/youfone)
[![github release](https://img.shields.io/github/v/release/geertmeersman/youfone?logo=github)](https://github.com/geertmeersman/youfone/releases)
[![github release date](https://img.shields.io/github/release-date/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/releases)
[![github last-commit](https://img.shields.io/github/last-commit/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/commits)
[![github contributors](https://img.shields.io/github/contributors/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/graphs/contributors)
[![github commit activity](https://img.shields.io/github/commit-activity/y/geertmeersman/youfone?logo=github)](https://github.com/geertmeersman/youfone/commits/main)

<!-- [END BADGES] -->

## Table of Contents

- [Youfone for Home Assistant](#youfone-for-home-assistant)
  - [Features](#features)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Using HACS (recommended)](#using-hacs-recommended)
    - [Manual](#manual)
  - [Contributions are welcome](#contributions-are-welcome)
  - [Troubleshooting](#troubleshooting)
    - [Enable debug logging](#enable-debug-logging)
    - [Disable debug logging and download logs](#disable-debug-logging-and-download-logs)
  - [Screenshots](#screenshots)
    - [Sensors](#sensors)
  - [Code origin](#code-origin)

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

**Click on this button:**

[![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=geertmeersman&repository=youfone&category=integration)

**or follow these steps:**

1. Simply search for `Youfone` in HACS and install it easily.
2. Restart Home Assistant
3. Add the 'Youfone' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Youfone username and password

### Manual

1. Copy the `custom_components/youfone` directory of this repository as `config/custom_components/youfone` in your Home Assistant installation.
2. Restart Home Assistant
3. Add the 'Youfone' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Youfone username and password

This integration will set up the following platforms.

| Platform  | Description                                      |
| --------- | ------------------------------------------------ |
| `youfone` | Home Assistant component for Youfone NL services |

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Troubleshooting

[![discord](http://invidget.switchblade.xyz/JpjHptEN2D)](https://discord.gg/JpjHptEN2D)

### Enable debug logging

To enable debug logging, go to Settings -> Devices & Services and then click the triple dots for the Youfone integration and click Enable Debug Logging.

![enable-debug-logging](https://raw.githubusercontent.com/geertmeersman/youfone/main/images/screenshots/enable-debug-logging.gif)

### Disable debug logging and download logs

Once you enable debug logging, you ideally need to make the error happen. Run your automation, change up your device or whatever was giving you an error and then come back and disable Debug Logging. Disabling debug logging is the same as enabling, but now you will see Disable Debug Logging. After you disable debug logging, it will automatically prompt you to download your log file. Please provide this logfile.

![disable-debug-logging](https://raw.githubusercontent.com/geertmeersman/youfone/main/images/screenshots/disable-debug-logging.gif)

## Screenshots

### Sensors

![Sensors](https://github.com/geertmeersman/youfone/raw/main/images/screenshots/sensors.png)

## Code origin

The code of this Home Assistant integration has been written by analysing the calls done by the Youfone website.

I have no link with Youfone
