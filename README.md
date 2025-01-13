# indipyterm

You may have Python programs implementing some form of data collection or control and wish to remotely operate such an instrument.

An associated package 'indipydriver' can be used to take your data, organise it into a data structure defined by the INDI protocol, and serve it on a port.

This indipyterm package provides a terminal client, which connects to the port, allowing you to view and control your instrument from a terminal session.

It can be installed from Pypi with:

pip install indipyterm

indipydriver and indipyterm communicate with the INDI protocol.

INDI - Instrument Neutral Distributed Interface.

See https://en.wikipedia.org/wiki/Instrument_Neutral_Distributed_Interface

The client can be run with

indipyterm [options]

or with

python3 -m indipyterm [options]

The package help is:

    usage: indipyterm [options]

    Terminal client to communicate to an INDI service.

    options:
      -h, --help   show this help message and exit
      --port PORT  Port of the INDI server (default 7624).
      --host HOST  Hostname/IP of the INDI server (default localhost).
      --version    show program's version number and exit

If you have a tool such as pipx or uv, then indipyterm can be installed into a virtual environment and run with a single command:

pipx run indipyterm

or

uvx indipyterm

A typical session would look like:

![Terminal screenshot](https://github.com/bernie-skipole/indipyterm/raw/main/indipyterm1.png)

and showing one device:

![Terminal screenshot](https://github.com/bernie-skipole/indipyterm/raw/main/indipyterm2.png)


The INDI protocol defines the format of the data sent, such as light, number, text, switch or BLOB (Binary Large Object). The client is general purpose, taking the format of switches, numbers etc., from the protocol.

The package can be installed from:

https://pypi.org/project/indipyterm

If installed from Pypi, then dependencies will automatically be pulled and installed, these are:

indipyclient - which generates and parses the INDI protocol.

textual - a library used to generate terminal interfaces.

Plus other packages which textual calls upon.

The indipydriver package which can be used to create instrument control, and serve the INDI protocol is available at:

https://pypi.org/project/indipydriver

https://github.com/bernie-skipole/indipydriver

https://indipydriver.readthedocs.io

The indipyclient package contains classes which may also be useful if you want to create your own client or client script, perhaps targeting a particular instrument:

https://pypi.org/project/indipyclient

https://github.com/bernie-skipole/indipyclient

https://indipyclient.readthedocs.io
