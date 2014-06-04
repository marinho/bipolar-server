# Bipolar Feature Toggle System

[![Build Status](https://drone.io/github.com/TDispatch/bipolar/status.png)](https://drone.io/github.com/TDispatch/bipolar/latest)

## Overview

**Bipolar** is a feature toggle micro service, a bit similar to **django-gargoyle**,
but with a deep difference: while django-gargoyle is a tool to switch features
on Django-based projects, Bipolar is a web service with an API with ability to
be used remotely by any language and framework.

That turns Bipolar a better tool to use in micro-service based architectures,
specially when there more than one language and framework in the whole system
and different frontend approaches.

## Entities

### Account

An account contains the other elements, with a shortcode and API key to be used for
authentation. That is very useful for a system with multiple services to serve.

### Feature

Each **feature** can be named or structured by the developer taste, as long as it
keeps a unique small-letters name for each account.

If a system has more than one place to enable or disable the same functionality
(e.g. business functions in a CRM), the functionality will be a single **Feature**
which is checked by more than one place in the code (can be different systems,
servers, languages, no matters).

### Qualifier

A **qualifier** is useful to set different permissions for the same features in an
account. A good example for it is when you have different **account types** in your
service (i.e. free and paying accounts), so, each account type is able to see the
features in different ways.

### Webhook

A **webhook** is and end point setup to receive the current account''s permissions
when something is updated (i.e. a new feature, a new qualifier, a permission is set
or unset, etc.)

Right now Bipolar supports only Pusher and raw post URLs.

## Software

Bipolar is written based on the following third party software:

- Python 2.7
- Django 1.6
- django-tastypie
- pusher
- jellyfish
- south
- requests
- responses

## License

Free and Open Source software based on **Gnu Public License v3**.

## Author

**Marinho Brandao** <name at gmail.com>

Released at first for **T Dispatch** - https://tdispatch.com

## To do

### Documentation

- Getting started
- Server installation
- Preparing Features, Qualifiers and Webhooks
- Using Bipolar
- Clients
- Examples

### Functions

- Update tests
- setup.py is not 100% working
- Django commands for server creation
- Way to deploy with custom settings and static folder
- User invitation
- Nice interface on home page
- Go client
- PHP client
- Ruby client
- JS client
