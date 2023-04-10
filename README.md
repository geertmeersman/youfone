<img src="https://github.com/geertmeersman/youfone/raw/main/images/brand/logo.png"
     alt="Youfone"
     align="right"
     style="width: 200px;margin-right: 10px;" />

# Youfone for Home Assistant

A Home Assistant integration allowing to monitor your Youfone usage

---

<!-- [START BADGES] -->
<!-- Please keep comment here to allow auto update -->

[![MIT License](https://img.shields.io/github/license/geertmeersman/youfone?style=for-the-badge)](https://github.com/geertmeersman/youfone/blob/master/LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![maintainer](https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github)](https://github.com/geertmeersman)
[![buyme_coffee](https://img.shields.io/badge/Buy%20me%20a%20Duvel-donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/geertmeersman)
[![discord](https://img.shields.io/discord/1094977038269546576?style=for-the-badge&logo=discord)](https://discord.gg/JpjHptEN2D)

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

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

1. Simply search for `Youfone` in HACS and install it easily.
2. Restart Home Assistant
3. Add the 'Youfone' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Youfone username and password

### Manual

1. Copy the `custom_components/youfone` directory of this repository as `config/custom_components/youfone` in your Home Assistant instalation.
2. Restart Home Assistant
3. Add the 'Youfone' integration via HA Settings > 'Devices and Services' > 'Integrations'
4. Provide your Youfone username and password

This integration will set up the following platforms.

| Platform  | Description                                           |
| --------- | ----------------------------------------------------- |
| `youfone` | Home Assistant component for Youfone BE & NL services |

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Troubleshooting

1. You can enable logging for this integration specifically and share your logs, so I can have a deep dive investigation. To enable logging, update your `configuration.yaml` like this, we can get more information in Configuration -> Logs page

```
logger:
  default: warning
  logs:
    custom_components.youfone: debug
```

## Screenshots

### Msisdn info

![Msisdn](https://github.com/geertmeersman/youfone/raw/main/images/screenshots/msisdn.png)

### Useraccount and Youcoins info

![Useraccount](https://github.com/geertmeersman/youfone/raw/main/images/screenshots/useraccount.png)

### Invoices

![Invoices](https://github.com/geertmeersman/youfone/raw/main/images/screenshots/invoices.png)

### Config flow

![Config flow](https://github.com/geertmeersman/youfone/raw/main/images/screenshots/config_flow.png)

![Config options](https://github.com/geertmeersman/youfone/raw/main/images/screenshots/config_options.png)
