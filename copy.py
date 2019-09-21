import sys
import os

m = 100
port = 3100
for i in range(m):
    cur = port + i * 3
    if not os.path.exists("./loopix/run_client%d.py" % cur):
        os.system('cp ./loopix/run_client.py ./loopix/run_client%d.py' % cur)