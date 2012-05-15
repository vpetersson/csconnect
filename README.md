# CSconnect

## About

csconnect.py is a Python-script that connects to [CloudSigma](http://www.cloudsigma.com)'s [API](http://cloudsigma.com/en/platform-details/the-api) and retreives the IPs for your servers. I wrote this tool, since I was tired of having to log into the web-interface to find out an IP for a given node. csconnect.py doesn't actually connect to your servers, it simply generates the connection string for you with the proper IPs.

## Requirements

* Python 2.6 (or later)
* PyCurl (pip install pycurl)
* [csshX](http://code.google.com/p/csshx/) ([brew](https://github.com/mxcl/homebrew) install csshx)
 * We'll use csshX to connect to more than one node.

## Usage

### Build a local database 

> python csconnect.py syncdb

### Generate a connection string

> python csconnect.py connect myNode

or 

> python csconnect.py connect myNode anotherNode ...

I've also built the tool to allow you to use match hostnames using a wildcard.

For instance, if we want to connect to 'server1', 'server2' and 'server3', we can run:

> python csconnect.py connect server

This will return all results matching 'server*'.
