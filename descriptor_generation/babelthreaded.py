import threading
import queue
import time
from random import randrange
import subprocess
from babelwork import BabelMolecule

def worker(kette):
    """Simple worker"""
    while True:
        try:
            name = threading.currentThread().getName()
            print('Thread: %s, current size of queue %s, time %s \n' %(name, kette.qsize(), time.strftime('%H:%M:%S')))
            time.sleep(randrange(1,10)*0.05)
            print(**kette.get())
            #m = Molecule(**kette.get())
            #m.routine()
            #subprocess.run(['obabel', '/Users/sandro/babeltest/cyclosporinA_iso.smi', '-O', '/Users/sandro/babeltest/test.sdf', '--gen3d', 'best', '--minimize', '--steps', '2000', '--sd'])#, stdout=subprocess.DEVNULL)
            kette.task_done()
            print('Thread: %s, current size of queue %s, finished time %s \n' % (name, kette.qsize(), time.strftime('%H:%M:%S')))
        except Exception:
            print('error with item')

# Generate Queue and fill
l =  [{'smiles':'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype':'iso'},
{'smiles':'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype':'iso'},
{'smiles':'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype':'iso'},
{'smiles':'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype':'iso'},
]
q = queue.Queue()
for i in l:
    print(i)
    q.put(i)


# Create threads
n_threads = 10
for thr in range(n_threads):
    thread = threading.Thread(name = 'Worker-'+str(thr), target=worker, args=(q,))
    #thread.setDaemon(True)
    thread.start()
    print('thread sksksksksk')


#waits until the queue is empty
q.join()
