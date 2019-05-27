
import os
import subprocess # just to call an arbitrary command e.g. 'ls'
from binascii import hexlify
import random
import sqlite3

host="127.0.0.1"
port=4100
group=0
provider_pre="Provider-"
mixnode_pre="Mix-"
client_pre="client-"

def run(cmd):
    return os.system(cmd)

def execute(cmd):
    return subprocess.check_output("%s; exit 0" % cmd, shell=True)

def get(f, t):
    os.system("cp %s ../%s" % (f, t))

def mkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

def cp(f, t):
    os.system("cp %s %s/" % (f, t))

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
        mkdir(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def storeProvidersNames():
    import petlib.pack
    pn = []
    for f in os.listdir('.'):
        if f.endswith(".bin"):
            with open(f, "rb") as infile:
                lines = petlib.pack.decode(infile.read())
                if lines[0] == "provider":
                    pn.append(lines[1])
    with open('providersNames.bi2', 'wb') as outfile:
        outfile.write(petlib.pack.encode(pn))

def getProvidersNames():
    import petlib.pack
    filedir = '../providersNames.bi2'
    with open(filedir, "rb") as infile:
        lines = petlib.pack.decode(infile.read())
    print lines
    return lines

c = 0
def deployMixnode(node):
    global c
    with cd(node['name']):
        cp("../*.py", ".")
        cp("../config.json", ".")
        N = hexlify(os.urandom(8))
        run("python setup_mixnode.py %d %s Mix%s %s" % (node['port'], node['host'], N, 0))
        get('publicMixnode.bin', 'publicMixnode-%s.bin' % N)
        c += 1

def deployProvider(node):
    with cd(node['name']):
        cp("../*.py", ".")
        cp("../config.json", ".")
        N = hexlify(os.urandom(8))
        run("python setup_provider.py %d %s Provider%s" % (node['port'], node['host'], N))
        get('publicProvider.bin', 'publicProvider-%s.bin' % N)

def deployClient(node):
    with cd(node['name']):
        cp("../*.py", ".")
        cp("../config.json", ".")
        N = hexlify(os.urandom(8))
        providers = getProvidersNames()
        prvName = random.choice(providers)
        run("python setup_client.py %d %s Client%s %s" % (node['port'], node['host'], N, prvName))
        get('publicClient.bin', 'publicClient-%s.bin' % N)


def readFiles():
    import petlib.pack

    # sys.path += ["../loopix"]
    # local("rm -f example.db")

    #import databaseConnect as dc
    from database_connect import DatabaseManager
    databaseName = "example.db"
    dbManager = DatabaseManager(databaseName)
    dbManager.create_users_table("Users")
    dbManager.create_providers_table("Providers")
    dbManager.create_mixnodes_table("Mixnodes")

    for f in os.listdir('.'):
        if f.endswith(".bin"):
            with open(f, 'rb') as fileName:
                lines = petlib.pack.decode(fileName.read())
                print 'Lines: ', lines
                if lines[0] == "client":
                    dbManager.insert_row_into_table('Users',
                        [None, lines[1], lines[2], lines[3],
                        sqlite3.Binary(petlib.pack.encode(lines[4])),
                        lines[5]])
                elif lines[0] == "mixnode":
                    dbManager.insert_row_into_table('Mixnodes',
                            [None, lines[1], lines[2], lines[3],
                            sqlite3.Binary(petlib.pack.encode(lines[5])), lines[4]])
                elif lines[0] == "provider":
                    dbManager.insert_row_into_table('Providers',
                        [None, lines[1], lines[2], lines[3],
                        sqlite3.Binary(petlib.pack.encode(lines[4]))])
                else:
                    assert False
    dbManager.close_connection()

def loaddir(instances):
    for instance in instances:
        cp("example.db", "%s/" % instance['name'])
    
PRE = "data-dir-"
nodes = [
    {'host': "127.0.0.1", 'port': 9999, 'name': "%smix-1" % PRE},
    {'host': "127.0.0.1", 'port': 9996, 'name': "%smix-2" % PRE},
    {'host': "127.0.0.1", 'port': 9998, 'name': "%spro-1" % PRE},
    {'host': "127.0.0.1", 'port': 9997, 'name': "%sclient-1" % PRE}
]

def deploy_all():
    
    run("rm -rf *.bin *.bi2 example.db data-dir-*")
    deployMixnode(nodes[0])
    deployMixnode(nodes[1])
    deployProvider(nodes[2])
    storeProvidersNames()
    deployClient(nodes[3])
    readFiles()
    loaddir(nodes)

def runMixnode(node):
    with cd(node['name']):
        run("twistd -y run_mixnode.py")
        pid = execute("cat twistd.pid")
        print "Run on %s with PID %s" % (node['host'], pid)

def runProvider(node):
    with cd(node['name']):
        run("twistd -y run_provider.py")
        pid = execute("cat twistd.pid")
        print "Run on %s with PID %s" % (node['host'], pid)

def runClient(node):
    with cd(node['name']):
        run('twistd -y run_client.py')
        pid = execute('cat twistd.pid')
        print "Run Client on %s with PID %s" % (node['host'], pid)

def run_all():
    runMixnode(nodes[0])
    runMixnode(nodes[1])
    runProvider(nodes[2])
    runClient(nodes[3])

deploy_all()
run_all()