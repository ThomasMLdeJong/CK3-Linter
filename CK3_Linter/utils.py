# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
# Modified work Copyright (c) 2020-2021 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

import glob
import importlib.util
import os
import re



LANGUAGE_TXT = "txt"

def load_plugins(directory, config):
    result = []
    fh = None

    for pluginfile in glob.glob(os.path.join(directory, '[A-Za-z]*.py')):

        pluginname = os.path.basename(pluginfile.replace('.py', ''))
        try:
            spec = importlib.util.spec_from_file_location(pluginname, pluginfile)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            obj = getattr(module, pluginname)(config)
            result.append(obj)
        finally:
            if fh:
                fh.close()
    return result


def get_rule_skips_from_line(line):
    rule_id_list = []
    if '# noqa' in line:
        noqa_text = line.split('# noqa')[1]
        rule_id_list = noqa_text.split()
    return rule_id_list


def get_rule_skips_from_text(text):
    rule_id_list = []
    for line in text.splitlines():
        rule_id_list.extend(get_rule_skips_from_line(line))

    return list(set(rule_id_list))


def get_file_type(file_name):
    extension = os.path.splitext(file_name)[1].lower()

    if extension == ".txt":
        return LANGUAGE_TXT
    return None

import re

def parse_triggers_log(filepath):
    """
    Reads a triggers.log file and parses entries separated by lines of dashes.
    Returns a list of dictionaries with keys: name, description, traits, scope.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split entries by delimiter lines consisting of at least 4 hyphens
    entries = re.split(r'\n-+\n', content.strip())

    triggers = []
    for entry in entries:
        lines = [line.strip() for line in entry.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        name_desc = lines[0].split(' - ', 1)
        name = name_desc[0].strip()
        description = name_desc[1].strip() if len(name_desc) > 1 else ''
        traits_match = re.match(r'Traits:\s*(.+)', lines[1])
        traits = [t.strip() for t in traits_match.group(1).split(',')] if traits_match else []
        scope_match = re.match(r'Supported Scopes:\s*(.+)', lines[2])
        scope = scope_match.group(1).strip() if scope_match else ''

        triggers.append({
            'name': name,
            'description': description,
            'traits': traits,
            'scope': scope
        })

    return triggers