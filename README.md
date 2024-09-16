# Home Assistant HiveOS

**HiveOS is now only accessible using API by paid farms. I haven't had time to develop this integration and, due to the API change, I'll officially stop development. I might pick this up in the future.**

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

Follow these steps to configure the integration:

1. Navigate to `Settings -> Devices & Services -> Integrations`.
2. Click `+ Add Integration`.
3. Find **HiveOS**.
4. [Generate a personal API token](https://id.hiveon.com/auth/realms/id/account/sessions) and provide it to the integration.

## Versioning

This project complies with [Semantic Versioning](https://semver.org/).

## Changelog

For a complete list of changes, and how to migrate between major versions, see [releases page](https://github.com/Ekman/home-assistant-hiveos/releases).
