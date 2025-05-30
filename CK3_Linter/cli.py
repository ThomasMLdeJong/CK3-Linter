# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
# Modified work Copyright (c) 2020-2024 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

from __future__ import print_function

import argparse
import os
import sys
import tempfile

from CK3_Linter import __version__
from CK3_Linter import formatters
from CK3_Linter.config import Configuration, CK3LintConfigError, default_rulesdir
from CK3_Linter.linter.collection import RulesCollection
from CK3_Linter.linter.runner import Runner

def run(args=None):
    """
    :param arg:
    :return:
    """
    parser = init_argument_parser()
    options = parser.parse_args(args if args is not None else sys.argv[1:])

    stdin_filename = None
    file_names = set(options.files)
    checked_files = set()

    if not sys.stdin.isatty():
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as stdin_tmpfile:
            stdin_tmpfile.write(sys.stdin.read())
            stdin_filename = stdin_tmpfile.name
            file_names.add(stdin_filename)

    options_dict = vars(options)
    try:
        config = Configuration(options_dict)
    except CK3ConfigError as exc:
        print(exc)
        return 2


    if not file_names and not (options.listrules or options.listtags):
        parser.print_help(file=sys.stderr)
        return 1

    collection = RulesCollection(config)
    for rulesdir in config.rulesdirs:
        collection.extend(RulesCollection.create_from_directory(rulesdir, config))

    if options.listrules:
        print(collection)
        return 0

    if options.listtags:
        print(collection.listtags())
        return 0

    formatter = initialize_formatter(config)

    problems = []
    for file_name in file_names:
        runner = Runner(collection, file_name, config, checked_files)
        problems.extend(runner.run())

    if stdin_filename:
        os.unlink(stdin_filename)

    if problems:
        sorted_problems = sort_problems(problems)
        formatter.process(sorted_problems)
        return 2
    return 0

def init_argument_parser():
    """
    """
    parser = argparse.ArgumentParser()

    # The files argument is optional as STDIN is always read
    parser.add_argument(dest='files', metavar='FILE', nargs='*', default=[],
                        help='one or more files or paths')

    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('-L', dest='listrules', default=False,
                        action='store_true', help="list all the rules")
    parser.add_argument('-r', action='append', dest='rulesdir',
                        default=[],
                        help="specify one or more rules directories using "
                             "one or more -r arguments. Any -r flags override "
                             "the default rules in %s, unless -R is also used."
                             % default_rulesdir)
    parser.add_argument('-R', action='store_true',
                        default=False,
                        dest='use_default_rules',
                        help="Use default rules in %s in addition to any extra "
                             "rules directories specified with -r. There is "
                             "no need to specify this if no -r flags are used."
                             % default_rulesdir)
    parser.add_argument('-t', dest='tags',
                        action='append',
                        default=[],
                        help="only check rules whose id/tags match these values")
    parser.add_argument('-T', dest='listtags', action='store_true',
                        help="list all the tags")
    parser.add_argument('-v', dest='verbosity', action='count',
                        help="Increase verbosity level",
                        default=0)
    parser.add_argument('-x', dest='skip_list', default=[], action='append',
                        help="only check rules whose id/tags do not " +
                             "match these values")
    parser.add_argument('--nocolor', '--nocolour', dest='colored',
                        default=hasattr(sys.stdout, 'isatty') and sys.stdout.isatty(),
                        action='store_false',
                        help="disable colored output")
    parser.add_argument('--force-color', '--force-colour', dest='colored',
                        action='store_true',
                        help="Try force colored output (relying on salt's code)")
    parser.add_argument('--exclude', dest='exclude_paths', action='append',
                        help='path to directories or files to skip. This option'
                             ' is repeatable.',
                        default=[])
    parser.add_argument('--json', dest='json', action='store_true', default=False,
                        help='parse the output as JSON')
    parser.add_argument('--severity', dest='severity', action='store_true', default=False,
                        help='add the severity to the standard output')

    return parser

def initialize_formatter(config):
    """

    :param config:
    :return:
    """
    if config.json:
        return formatters.JsonFormatter()
    elif config.severity:
        return formatters.SeverityFormatter(config.colored)
    return formatters.Formatter(config.colored)

def sort_problems(problems):
    """
    :param problems:
    :return:
    """
    problems.sort(
        key=lambda problem: (
            problem.filename,
            problem.linenumber,
            problem.rule.id
        )
    )
    return problems
