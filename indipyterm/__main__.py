

import sys, argparse, asyncio, pathlib, logging

sys.path.insert(0, "/home/bernard/git/indipyclient")



from . import version
from .indipyterm import IPyTerm

from .connections import make_connection





def main():
    """The commandline entry point to run the terminal client."""

    # Create the initial server connection
    make_connection()

    # run the IPyTerm app
    app = IPyTerm()
    app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
