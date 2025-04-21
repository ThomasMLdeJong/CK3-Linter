# -*- coding: utf-8 -*-
# Copyright (c) 2020 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

import os
import sys
import pathspec
import yaml

import CK3_Linter.utils

default_rulesdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "rules")

class CK3LintConfigError:
    pass

class Configuration(object):
    def __init__(self, options={}):
        self._options = options
        config = options.get('c')

        if config is None:
            config = get_config_path()

        if config and os.path.exists(config):
            with open(config, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = None

        self._parse(content)

    def _parse(self, content):
        config = {}

        if content:
            try:
                config = yaml.safe_load(content)
            except yaml.YAMLError as exc:
                raise CK3LintConfigError(
                    "invalid config: {}".format(exc)
                ) from exc

        self.verbosity = self._options.get('verbosity', 0)
        if 'verbosity' in config:
            self.verbosity += config['verbosity']

        self.exclude_paths = self._options.get('exclude_paths', [])
        if 'exclude_paths' in config:
            self.exclude_paths += config['exclude_paths']

        skip_list = self._options.get('skip_list', [])
        if 'skip_list' in config:
            skip_list += config['skip_list']
        skip = set()
        for s in skip_list:
            skip.update(str(s).split(','))
        self.skip_list = frozenset(skip)

        self.tags = self._options.get('tags', [])
        if 'tags' in config:
            self.tags += config['tags']
        if isinstance(self.tags, str):
            self.tags = self.tags.split(',')

        use_default_rules = self._options.get('use_default_rules', False)
        if 'use_default_rules' in config:
            use_default_rules = use_default_rules or config['use_default_rules']

        rulesdir = self._options.get('rulesdir', [])
        if 'rulesdir' in config:
            rulesdir += config['rulesdir']

        if use_default_rules:
            self.rulesdirs = rulesdir + [default_rulesdir]
        else:
            self.rulesdirs = rulesdir or [default_rulesdir]

        self.colored = self._options.get(
            'colored',
            hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        )

        self.json = self._options.get('json', False)
        if 'json' in config:
            self.json = config['json']

        self.severity = self._options.get('severity', False)
        if 'severity' in config:
            self.severity = config['severity']

        self.rules = {}
        if 'rules' in config and isinstance(config['rules'], dict):
            for name, rule in config['rules'].items():
                self.rules[str(name)] = {}

                if 'ignore' not in rule:
                    continue

                if not isinstance(rule['ignore'], str):
                    raise SaltLintConfigError(
                        'invalid config: ignore should contain file patterns'
                    )

                self.rules[str(name)]['ignore'] = pathspec.PathSpec.from_lines(
                    'gitwildmatch', rule['ignore'].splitlines())

    def is_file_ignored(self, filepath, rule):
        rule = str(rule)
        if rule not in self.rules or 'ignore' not in self.rules[rule]:
            return False
        return self.rules[rule]['ignore'].match_file(filepath)


def get_config_path():
    """Return local configuration file."""
    dirname = basename = os.getcwd()
    while basename:
        filename = os.path.abspath(os.path.join(dirname, ".salt-lint"))
        if os.path.exists(filename):
            return filename
        if os.path.exists(os.path.abspath(os.path.join(dirname, ".git"))):
            return None
        (dirname, basename) = os.path.split(dirname)
    return None

