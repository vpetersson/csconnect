#!/usr/bin/env python
"""
A tool to manage and connect to virtual servers at CloudSigma.

@author Viktor Petersson
"""
import requests, os, pickle, sys, ConfigParser

config = ConfigParser.ConfigParser()
conf_dir = os.path.join(os.getenv("HOME"), ".csconnect")
conf_file = os.path.join(conf_dir, 'csconnect.cfg')
db = os.path.join(conf_dir, 'cache.pkl')


# Check if the config-folder exist. 
# If not, create it.
if not os.path.isdir(conf_dir):
    os.mkdir(conf_dir)

# Make sure the config-file is in place
if not os.path.isfile(conf_file):
    print "Config file is missing. Exiting."
    print "Please edit and copy the example file to %s" % conf_file
    sys.exit()
else:
    config.read(conf_file)

api_user = config.get('Main', 'api_user')
api_pass = config.get('Main', 'api_pass')
api_url = config.get('Main', 'api_url')
ssh_user = config.get('Main', 'ssh_user')

def make_api_call(call):
    r = requests.get(api_url + call, auth=(api_user, api_pass))

    if r.status_code == 200:
        return r.content.strip()
    else:
        return None

def get_server_list():
    server_list = make_api_call('/servers/list')
    if server_list:
        return server_list.strip().split('\n')
    else:
        return None

def get_server_info(uuid):
    server_info = make_api_call('/servers/' + uuid + '/info')
    if server_info:
        explode = server_info.split('\n')
        return explode
    else:
        return None

# Extract the name and the IP of 'nic0'
def extract_info(server_info):
    for line in server_info:
        if ("nic:0:dhcp" or "nic:0:static") in line:
            explode_ip = line.split(' ')
            ip = explode_ip[-1]
        if "name" in line:
            explode_name = line.split(' ')
            name = explode_name[-1]
    return [name, ip]

def build_db():
    servers = {}
    server_list = get_server_list()
    for uuid in server_list:
        info = get_server_info(uuid)
        lookup = extract_info(info)
        if not lookup[1] == "auto":
            servers[lookup[0]] = lookup[1]
    return servers

def write_db():
    server_db = build_db()

    output = open(db, 'wb')
    pickle.dump(server_db, output)
    output.close()

def search_db(string, db):
    hits = []
    for record in db:
        if string.lower() in record.lower():
            ip = db[record]
            hits.append(ip)
    return hits

def read_db():
    input = open(db, 'rb')
    server_db = pickle.load(input)
    input.close()
    return server_db

if len(sys.argv) == 1:
    print """
    Usage:
    csconnect.py syncdb
    csconnect connect MyServer
    """
    sys.exit()


if sys.argv[1] == "syncdb":
    write_db()

elif sys.argv[1] == "connect":
    result = []
    server_db = read_db()

    for node in sys.argv[2:]:
        query = search_db(node, server_db)
        result.append(query)

    # Clever workaround (http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python)
    # Also, filter out duplicates using a 'set'
    flat_list = set(sum(result, []))

    connection_string = " ".join(flat_list)
    hits = len(flat_list)

    if hits == 0:
        print "No matches found"

    # One hit -- use ssh
    elif hits == 1:
        print "ssh -l " + ssh_user + " -o StrictHostKeyChecking=no " + connection_string

    # More than one hit -- use csshX
    else:
        print "echo \"" + connection_string + "\" | " + "csshX --login " + ssh_user + " --ssh_args=\"-o StrictHostKeyChecking=no\" --hosts -"


elif sys.argv[1] == "dump":
    server_db = read_db()

    print "==Node name==" + "\t\t" + "==IP=="
    for item in server_db:
        print item + "\t\t" + server_db[item]

else:
    print "Invalid command."


