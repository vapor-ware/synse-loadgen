#!/usr/bin/env python3
"""Entry point script for running Synse LoadGen."""

import asyncio

from synse_loadgen.app import run


def main() -> None:
    asyncio.get_event_loop().run_until_complete(run())


if __name__ == '__main__':
    main()
