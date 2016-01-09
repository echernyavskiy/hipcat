#!/usr/bin/env python3

"""
Pipe text to a HipChat room.
"""

import configparser
import json
import os
import sys

import click
import requests


APP_NAME = 'hipcat'


class UserError(Exception):
    pass


class ConfigurationError(UserError):
    pass


class Config(object):
    def load(self):
        config_paths = [
            os.path.expanduser('~/.hipcat.ini'),
            os.path.join(click.get_app_dir(APP_NAME), 'config.ini'),
            os.path.join(
                click.get_app_dir(APP_NAME, force_posix=True), 'config.ini'
            ),
        ]
        config = configparser.ConfigParser()
        configs_found = config.read(config_paths)
        if not configs_found:
            raise ConfigurationError("""
Missing configuration!

You must provide configuration in one of the following places:

""" + "\n".join(' * {}'.format(path) for path in config_paths) + """
"""
            )
        self.config = config

        return self

    @property
    def hipchat_token(self):
        token = self.config.get('hipchat', 'access_token', fallback=None)
        if not token:
            raise ConfigurationError(
"""
Configuration error!

You must provide an 'access_token' in your configuration's 'hipchat' section.
"""
            )
        return token

    @property
    def base_url(self):
        return self.config.get('hipchat', 'base_url', fallback='https://www.hipchat.com').rstrip('/')



@click.command(help=__doc__)
@click.version_option()
@click.argument('room')
@click.option('-m', '--message')
def main(room, message):
    try:
        config = Config().load()

        url = '{config.base_url}/v2/room/{room_id_or_name}/message'.format(
            config=config,
            room_id_or_name=room,
        )
        message = message or sys.stdin.read()
        if message:
            response = requests.post(
                url,
                headers={
                    'Authorization': 'Bearer {}'.format(config.hipchat_token),
                    'Content-Type': 'application/json',
                },
                data=json.dumps({
                    'message': message
                }),
            ).json()
            if 'error' in response:
                print(response['error']['message'], file=sys.stderr)
                exit(1)
    except KeyboardInterrupt:
        exit(1)
    except UserError as user_error:
        print(user_error, file=sys.stderr)
        exit(2)
