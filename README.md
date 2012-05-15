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

This will give you an output similar to this:

> ssh -l mysshuser -o StrictHostKeyChecking=no 123.123.123.123

To connect to multiple nodes, simply provide them in a space-separated list.

> python csconnect.py connect myNode anotherNode ...

This will return something like:

> echo -e "123.123.123.123\n124.124.124.124" | csshX --login mysshuser --ssh_args="-o StrictHostKeyChecking=no" --hosts -

I've also built the tool to allow you to use match hostnames using a wildcard.

For instance, if we want to connect to 'server1', 'server2' and 'server3', we can run:

> python csconnect.py connect server

This will return all results matching 'server*'.

It's also worth pointing out that I pass "StrictHostKeyChecking=no" as an argument to SSH. The reason for this is that if you spin up and down nodes frequently on CloudSigma, chances are that the IPs will be recycled between nodes. By default, SSH will (rightfully) reject that connection to avoid [Man-in-the-Middle attacks](http://en.wikipedia.org/wiki/Man-in-the-middle_attack). Since we retreive IP directy from CloudSigma's API, we can be fairly certain that the IP we received is the correct IP. Yet, if you're paranoid, feel free to *not* append this flag. 