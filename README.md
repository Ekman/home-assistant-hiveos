# Home Assistant HiveOS

[![CircleCI](https://circleci.com/gh/Ekman/home-assistant-hiveos/tree/master.svg?style=svg)](https://circleci.com/gh/Ekman/home-assistant-hiveos/tree/master)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Control your HiveOS crypto miners using Home Assistant.

**Under development and not ready for production. Expect breaking changes.**

## Installation

Install using [Home Assistant Community Store (HACS)](https://hacs.xyz/).

**If you don't already have HACS installed** then follow these steps:

1. [Install HACS](https://hacs.xyz/docs/setup/prerequisites)
2. [Configure HACS](https://hacs.xyz/docs/configuration/basic)

**Once HACS is installed on your Home Assistance** then follow these steps:

1. Add `https://github.com/Ekman/home-assistant-hiveos` as a [custom repository in HACS](https://hacs.xyz/docs/faq/custom_repositories/)
2. Install `HiveOS` using HACS
3. Reboot Home Assistant

## Configuration

Navigate to `Settings -> Devices & Services -> Integrations`. Click `+ Add Integration`, find and configure HiveOS. You will need to provide a personal API token to the integration, which you can create [here](https://id.hiveon.com/auth/realms/id/account/sessions).

## Versioning

This project complies with [Semantic Versioning](https://semver.org/).

## Changelog

For a complete list of changes, and how to migrate between major versions, see [releases page](https://github.com/Ekman/home-assistant-hiveos/releases).
