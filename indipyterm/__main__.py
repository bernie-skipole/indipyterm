

import sys, argparse

from . import version
from .indipyterm import IPyTerm
from .connections import make_connection



def main():
    """The commandline entry point to run the terminal client."""

    parser = argparse.ArgumentParser(usage="indipyterm [options]",
                                     description="Terminal client to communicate to an INDI service.")
    parser.add_argument("--port", type=int, default=7624, help="Port of the INDI server (default 7624).")
    parser.add_argument("--host", default="localhost", help="Hostname/IP of the INDI server (default localhost).")
    parser.add_argument("--version", action="version", version=version)
    args = parser.parse_args()

    # Create the initial server connection
    make_connection(host=args.host, port=args.port)

    # run the IPyTerm app
    app = IPyTerm()
    app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
