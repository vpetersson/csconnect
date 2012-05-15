import pycurl, re, cStringIO, sys, subprocess, pickle, copy

login = 'you@yourdomain.com:yourpassword' # For API access
apiurl = "https://api.zrh.cloudsigma.com" # Zurich-datacenter
#apiurl = "api.lvs.cloudsigma.com"  # Las Vegas-datacenter
username = 'yourusername' # For SSH

# Function to get all server UUIDs
def getServerList():
    buf = cStringIO.StringIO()
    c = pycurl.Curl()
    url = apiurl + '/servers/list'
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.CONNECTTIMEOUT, 5)
    c.setopt(c.TIMEOUT, 8)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.USERPWD, login)
    c.perform()
    return buf.getvalue()
    buf.close()

# Function to fetch server info based on an UUID
def getServerInfo(UUID):
    buf = cStringIO.StringIO()
    c = pycurl.Curl()
    url = apiurl + '/servers/%s/info' % (UUID)
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.CONNECTTIMEOUT, 5)
    c.setopt(c.TIMEOUT, 8)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.USERPWD, login)
    c.perform()
    return buf.getvalue()
    buf.close()

# List search function from:
# http://stackoverflow.com/questions/2170900/get-first-list-index-containing-sub-string-in-python
def findInList(the_list, substring):
    for i, s in enumerate(the_list):
      if substring in s:
        return i
    return -1

# Make a regex-search of hits in a list
def looseNameLookup(the_list, string):
    for keys in the_list.keys():
        searchstring = re.findall('^'+string+'.*', keys)
        for hit in searchstring:
            if len(hit) > 0:
                return hit

def exitFunction():
    print "\n\n" + 40 * "-"
    print "For initial sync, or to refresh the database, run:"
    print "\t%s syncdb\n" % (sys.argv[0])    
    print "To connect to a node, run:"
    print "\t%s connect server1\n" % (sys.argv[0])    
    print "To connect to multiple servers, provide a space-separated list."
    print "\n\n" + 40 * "-"
    sys.exit(1)

# Verify input
if len(sys.argv) == 1:
    exitFunction()

## Now to the real action
# Fetch or refresh the local database
if sys.argv[1] == 'syncdb': 

    # Strip out all whitespace and split by newlines
    serverUUIDs = getServerList().strip().split('\n')

    # Resolve all UUIDs
    serverlist = {}
    for x in serverUUIDs:
        server = getServerInfo(x).split('\n')
        servername = re.sub('name\s+', '', server[findInList(server, 'name')]).lower()
        # We're grabbing the IP of the first NIC and going to asume that is the one we want.
        serverip = re.sub('nic:0:dhcp\s+', '', server[findInList(server, 'nic:0:dhcp')])
        serverlist[servername] = serverip

    # Write 'serverlist' to file
    writefile = open('serverlist.pkl', 'wb')
    pickle.dump(serverlist, writefile)
    writefile.close()

# Connect to a node.
elif sys.argv[1] == 'connect':
    if len(sys.argv) == 2:
        exitFunction()
    else:
        # Read database from file and copy the content
        openfile = open('serverlist.pkl', 'rb')
        serverinputlist = pickle.load(openfile)
        serverlist = copy.copy(serverinputlist)
        openfile.close()
    
        # Initiate an emtpy dictionary
        connectionlist = []
    
        # Process the input nodes
        for arg in sys.argv[2:]:
            arglower = arg.lower()
            while looseNameLookup(serverlist, arglower):
                try:
                    hit = looseNameLookup(serverlist, arglower)
                    connectionlist.append(serverlist.get(hit))
                    serverlist.pop(hit)
                except:
                    pass
       
        # This will be the SSH connection string.
        sshinput = " ".join(connectionlist)
        
        # If only one server is provided, use ssh from terminal, 
        # otherwise use csshX. 
        # We also append "StrictHostKeyChecking" since an IP can move between nodes on reboot. 
        # Yes, I know this opens up for MITM-attacks, so feel free to not append that.
        if len(connectionlist) == 1:
            print("ssh -l " + username + " -o StrictHostKeyChecking=no " + sshinput)
        else:
            print("echo -e \"" + sshinput.replace(' ', '\\n') + "\" | " + "csshX --login " + username + " --ssh_args=\"-o StrictHostKeyChecking=no\" --hosts -")
else:
    exitFunction()