# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
# Modified work Copyright (c) 2020 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

from CK3_Linter.linter.rule import Rule

class TrailingWhiteSpace(Rule):
    id = 'CK3-001'
    shortdesc = 'Trailing whitespace'
    description = ('There should not be any trailing whitespace in this file')
    severity = 'INFO'
    tags = ['formatting']
    version_added = 'v0.0.1'

    def match(self, file, line):
        line = line.replace("\r", "")
        return line.rstrip() != line