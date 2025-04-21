# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Will Thames <will@thames.id.au>
# Modified work Copyright (c) 2020 Warpnet B.V.
# Modified work Copyright (c) 2025 Thomas de Jong <Thomasmldejong@gmail.com>

import sys
import errno

from CK3_Linter.cli import run

if __name__ == "__main__":
    try:
        sys.exit(run())
    except IOError as exc:
        if exc.errno != errno.EPIPE:
            raise
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
