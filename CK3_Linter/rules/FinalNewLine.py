# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
# Modified work Copyright (c) 2020 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

from CK3_Linter.linter.rule import Rule
from CK3_Linter.linter.match import Match

class FinalNewLine(Rule):
    id = 'CK3-002'
    shortdesc = 'File should end with a newline'
    description = 'All Salt state files should end with a final newline'
    severity = 'INFO'
    tags = ['formatting']
    version_added = 'v0.0.1'

    def matchlastline(self, file, text):
        lines = text.split("\n")
        last_line = lines[-1]

        if last_line != '' and not text.endswith('\n'):
            return False
        return True

    def matchlines(self, file, text):
        matches = super().matchlines(file, text)

        if not self.matchlastline(file, text):
            matches.append(Match(len(text.split("\n")), text.split("\n")[-1], file['path'], self, "File should end with a newline"))

        return matches
