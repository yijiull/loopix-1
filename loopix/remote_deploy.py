
from remote.remote_execute import unique_execute, execute, connect, local_execute, run_once
from binascii import hexlify
import os
import random
import sqlite3

mixes = [
    {'host': "127.0.0.1", 'port': 9999, 'name': "mix-1"},
    {'host': "127.0.0.1", 'port': 9996, 'name': "mix-2"},
]

providers = [
    {'host': "127.0.0.1", 'port': 9998, 'name': "pro-1"},
]

clients = [
    {'host': "127.0.0.1", 'port': 9997, 'name': "client-1"},
    {'host': "127.0.0.1", 'port': 9995, 'name': "client-2"},
]

instances = mixes + providers + clients

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
    filedir = 'providersNames.bi2'
    with open(filedir, "rb") as infile:
        lines = petlib.pack.decode(infile.read())
    print lines
    return lines

def loaddir():
    for instance in instances:
        with connect(instance['host'], instance['name'], False) as r:
            r.put("example.db", "loopix/loopix/")

# install dependency
# unique_execute("pip install numpy pytest twisted "\
    # "msgpack-python petlib sphinxmix==0.0.6 matplotlib scipy scapy pybloom",
    # is_shared=False)


# setup repo
# execute("git clone git@github.com:jianyu-m/loopix.git")

def deployMixnode():
    for idx, mix in enumerate(mixes):
        with connect(mix['host'], mix['name'], False) as r:
            r.execute("git clone git@github.com:jianyu-m/loopix.git")
            r.put("config.json", "loopix/loopix/")
            N = hexlify(os.urandom(8))
            r.execute("cd loopix/loopix/; python setup_mixnode.py %d %s Mix%s %s" % (mix['port'], mix['host'], N, 0))
            r.get('loopix/loopix/publicMixnode.bin', 'publicMixnode-%s.bin' % N)

def deployProvider():
    for idx, provider in enumerate(providers):
        with connect(provider['host'], provider['name'], False) as r:
            r.execute("git clone git@github.com:jianyu-m/loopix.git")
            r.put("config.json", "loopix/loopix/")
            N = hexlify(os.urandom(8))
            r.execute("cd loopix/loopix/; python setup_provider.py %d %s Provider%s" % (provider['port'], provider['host'], N))
            r.get('loopix/loopix/publicProvider.bin', 'publicProvider-%s.bin' % N)

def deployClient():
    for idx, client in enumerate(clients):
        with connect(client['host'], client['name'], False) as r:
            r.execute("git clone git@github.com:jianyu-m/loopix.git")
            N = hexlify(os.urandom(8))
            all_providers = getProvidersNames()
            prvName = random.choice(all_providers)
            r.execute("cd loopix/loopix/; python setup_client.py %d %s Client%s %s" % (client['port'], client['host'], N, prvName))
            r.get('loopix/loopix/publicClient.bin', 'publicClient-%s.bin' % N)

@run_once
def deploy_all():
    local_execute("rm -rf *.bin *.bi2 example.db")
    deployMixnode()
    deployProvider()
    storeProvidersNames()
    deployClient()
    readFiles()
    loaddir()

def runMixnode():
    for mix in mixes:
        with connect(mix['host'], mix['name'] + "/loopix/loopix/", False) as r:
            r.execute("twistd -y run_mixnode.py")

def runProvider():
    for provider in providers:
        with connect(provider['host'], provider['name'] + "/loopix/loopix/", False) as r:
            r.execute("twistd -y run_provider.py")

def runClient():
    for client in clients:
        with connect(client['host'], client['name'] + "/loopix/loopix/", False) as r:
            r.execute("python run_client.py")

def run_all():
    runMixnode()
    runProvider()
    runClient()

deploy_all()
run_all()
