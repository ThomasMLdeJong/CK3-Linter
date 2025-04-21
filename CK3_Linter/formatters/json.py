# -*- coding: utf-8 -*-
# Copyright (c) 2013-2018 Will Thames <will@thames.id.au>
# Copyright (c) 2018 Ansible by Red Hat
# Modified work Copyright (c) 2020 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

import json

from CK3_Linter.formatters.base import BaseFormatter


class JsonFormatter(BaseFormatter):
    def process(self, problems, *args, **kwargs):
        items = []
        for problem in problems:
            items.append(self.format(problem))
        print(json.dumps(items))

    def format(self, problem):
        return {
            'id': problem.rule.id,
            'message': problem.message,
            'filename': problem.filename,
            'linenumber': problem.linenumber,
            'line': problem.line,
            'severity': problem.rule.severity,
        }