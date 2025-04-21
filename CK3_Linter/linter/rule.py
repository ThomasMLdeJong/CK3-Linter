# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
# Modified work Copyright (c) 2020 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

from typing import List, Optional
import re

from CK3_Linter.utils import get_rule_skips_from_line, get_file_type
from CK3_Linter.linter.match import Match
from CK3_Linter.utils import LANGUAGE_TXT


class Rule(object):

    id: Optional[str] = None
    shortdesc: Optional[str] = None
    description: Optional[str] = None
    languages: List[str] = []
    match = None
    matchtext = None

    def __init__(self, config=None):
        self.config = config

    def __repr__(self):
        return self.id + ": " + self.shortdesc

    def verbose(self):
        return self.id + ": " + self.shortdesc + "\n " + self.description

    @staticmethod
    def unjinja(text):
        return re.sub(r"{{[^}]*}}", "JINJA_VAR", text)

    def is_valid_language(self, file):
        """
        Returns True if the file type is in the supported languages or no
        language is specified for the linting rule and False otherwise.

        The file type is determined based upon the file extension.
        """
        if not self.languages or get_file_type(file["path"]) in self.languages:
            return True
        return False

    def matchlines(self, file, text):
        matches = []

        if not self.match:
            return matches

        if not self.is_valid_language(file):
            return matches

        for (prev_line_no, line) in enumerate(text.split("\n")):
            if line.lstrip().startswith('#'):
                continue

            rule_id_list = get_rule_skips_from_line(line)
            if self.id in rule_id_list:
                continue

            result = self.match(file, line)
            if not result:
                continue
            message = None
            if isinstance(result, str):
                message = result
            matches.append(Match(prev_line_no+1, line,
                                 file['path'], self, message))

        return matches

    def matchfulltext(self, file, text):
        matches = []
        if not self.matchtext:
            return matches

        if not self.is_valid_language(file):
            return matches

        results = self.matchtext(file, text)

        for line, section, message in results:
            matches.append(Match(line, section, file['path'], self, message))

        return matches

    def matchlastline(self, file, text):
        lines = text.split("\n")
        last_line = lines[-1].strip()

        if not last_line:
            return []

        matches = []

        if not self.is_valid_language(file):
            return matches

        if self.match:
            result = self.match(file, last_line)
            if result:
                message = None
                if isinstance(result, str):
                    message = result
                matches.append(Match(len(lines), last_line, file['path'], self, message))

        return matches

class CK3Rule(Rule):
    """
    CK3Rule is a structured rule meant for CK3-style Paradox script files.

    Instead of matching line-by-line (like SaltLint), it assumes a parsed
    tree structure that exposes triggers with metadata: key, value, operator, scope, etc.
    """

    severity: str = 'MEDIUM'
    languages = [LANGUAGE_TXT]
    tags = ['ck3']

    def match(self, parsed_file):
        """
        Override this method in subclasses to check trigger structure.
        'parsed_file' should provide a way to traverse all triggers with metadata.
        """
        return []

    def error(self, node, message):
        """
        Generate a Match object from a parsed trigger node.
        Assumes the node has line/section/path metadata.
        """
        return Match(
            linenumber=node.line,
            line=node.section,
            filename=node.path,
            rule=self,
            message=message
        )