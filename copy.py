import sys
import os

m = 100
port = 3100
for i in range(m):
    cur = port + i * 3
<<<<<<< HEAD
    if not os.path.exists("./loopix/run_client%d.py" % cur):
        os.system('cp ./loopix/run_client.py ./loopix/run_client%d.py' % cur)
=======
    if not os.path.exists("./loopix/run_mixnode_%d.py" % cur):
        os.system('cp ./loopix/run_mixnode.py ./loopix/run_mixnode_%d.py' % cur)
>>>>>>> 39e274a117576fd0a8fea489f1e324ef7f3ef15d
