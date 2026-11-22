<img src="https://github.com/geertmeersman/youfone/raw/main/images/brand/logo.png"
     alt="Youfone"
     align="right"
     style="width: 200px;margin-right: 10px;" />

# Youfone for Home Assistant

A Home Assistant integration allowing to monitor your Youfone usage

> **Note:** To avoid IP blacklisting, the update interval is set to a minimum of 2 hours (configurable). On restart, Home Assistant loads data from local storage and refreshes after the configured interval.

### Features

- 📱 Mobile data usage sensors
- 🌍 World roaming bundle sensors
- 📞 Voice & SMS sensors
- 💰 Subscription price sensor
- 📅 Remaining days sensor
- 👤 User account information

---

<!-- [START BADGES] -->
<!-- Please keep comment here to allow auto update -->

[![maintainer](https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github)](https://github.com/geertmeersman)
[![buyme_coffee](https://img.shields.io/badge/Buy%20me%20an%20Omer-donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/geertmeersman)


[![MIT License](https://img.shields.io/github/license/geertmeersman/youfone?style=flat-square)](https://github.com/geertmeersman/youfone/blob/master/LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=flat-square)](https://github.com/hacs/integration)

[![Open your Home Assistant instance and open the repository inside the Home Assistant Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=geertmeersman&repository=youfone&category=integration)

[![GitHub issues](https://img.shields.io/github/issues/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/issues)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/geertmeersman/youfone.svg)](http://isitmaintained.com/project/geertmeersman/youfone)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/geertmeersman/youfone.svg)](http://isitmaintained.com/project/geertmeersman/youfone)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/geertmeersman/youfone/pulls)

[![Hacs and Hassfest validation](https://github.com/geertmeersman/youfone/actions/workflows/validate.yml/badge.svg)](https://github.com/geertmeersman/youfone/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/Python-FFD43B?logo=python)](https://github.com/geertmeersman/youfone/search?l=python)

[![manifest version](https://img.shields.io/github/manifest-json/v/geertmeersman/youfone/master?filename=custom_components%2Fyoufone%2Fmanifest.json)](https://github.com/geertmeersman/youfone)
[![github release](https://img.shields.io/github/v/release/geertmeersman/youfone?logo=github)](https://github.com/geertmeersman/youfone/releases)
[![github release date](https://img.shields.io/github/release-date/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/releases)
[![Downloads (latest release)](https://img.shields.io/github/downloads/geertmeersman/youfone/latest/total)](https://github.com/geertmeersman/youfone/releases/latest)
[![github last-commit](https://img.shields.io/github/last-commit/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/commits)
[![github contributors](https://img.shields.io/github/contributors/geertmeersman/youfone)](https://github.com/geertmeersman/youfone/graphs/contributors)
[![github commit activity](https://img.shields.io/github/commit-activity/y/geertmeersman/youfone?logo=github)](https://github.com/geertmeersman/youfone/commits/main)

<!-- [END BADGES] -->

## Table of Contents

- [Youfone for Home Assistant](#youfone-for-home-assistant)
  - [Features](#features)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Using the Home Assistant Marketplace (recommended)](#using-the-home-assistant-marketplace-recommended)
    - [Manual](#manual)
  - [Entities](#entities)
  - [Contributions are welcome](#contributions-are-welcome)
  - [Troubleshooting](#troubleshooting)
    - [Enable debug logging](#enable-debug-logging)
    - [Disable debug logging and download logs](#disable-debug-logging-and-download-logs)
  - [Screenshots](#screenshots)
  - [Code origin](#code-origin)

## Installation

### Using the [Home Assistant Marketplace](https://www.home-assistant.io/integrations/marketplace/) (recommended)

**Click on this button:**

[![Open your Home Assistant instance and open the repository inside the Home Assistant Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=geertmeersman&repository=youfone&category=integration)

**or follow these steps:**

1. Simply search for `Youfone` in the Home Assistant Marketplace and install it easily.
2. Restart Home Assistant
3. Add the 'Youfone' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Youfone username and password

### Manual

1. Copy the `custom_components/youfone` directory into your `config/custom_components/` folder
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for `Youfone` and follow the configuration steps

## Entities

Each SIM card is represented as a separate device. The following sensors are created per SIM:

### SIM subscription sensors

| Entity | Description | Unit | Attributes |
| ------ | ----------- | ---- | ---------- |
| `sensor.youfone_customer` | Account holder name | – | Full customer info |
| `sensor.youfone_sim_subscription_<msisdn>` | Active subscription name | – | Full subscription info |
| `sensor.youfone_sim_subscription_price_<msisdn>` | Monthly subscription price | € | – |
| `sensor.youfone_data_<msisdn>` | Mobile data usage | % | Used, total, unlimited flag, msisdn |
| `sensor.youfone_voice_<msisdn>` | Voice & SMS usage | % | Used, total, unlimited flag, msisdn |
| `sensor.youfone_remaining_days_<msisdn>` | Days remaining in billing period | days | Period percentage |

### World roaming sensors

Shown only when a separately purchased world roaming bundle is active on the account (`SIM_ROAMING` card type).

| Entity | Description | Unit | Attributes |
| ------ | ----------- | ---- | ---------- |
| `sensor.youfone_sim_roaming_data_<msisdn>` | Roaming bundle data usage | % | Bundle name, destination (e.g. Marokko), used MB, total MB, due date, remaining days |

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Troubleshooting

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
