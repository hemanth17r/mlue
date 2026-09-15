#!/usr/bin/env python3
"""MLUE CLI & Preview Entrypoint

Provides direct execution and backward-compatibility forwarding to mlue.__main__.
"""

from mlue.__main__ import main

if __name__ == "__main__":
    main()
