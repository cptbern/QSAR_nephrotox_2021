from multiprocessing import Lock, Process, Queue, current_process, Manager, Pool, cpu_count
import time
import queue # imported for using queue.Empty exception
from babelwork import BabelMolecule
import logging
from sanbase.filework.spreadsheet import Spreadsheet
import pandas as pd

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
#logger.addHandler(c_handler)
logger.addHandler(f_handler)


def updatedrug(pandasobj, calcs):
    pandasobj['energypreopt'] = calcs['energypreopt']
    pandasobj['energyminimized'] = calcs['energyminimized']
    pandasobj['error'] = calcs['error']
    pandasobj['structurestring'] = calcs['structurestring']

    return pandasobj

def worker(tasks_to_accomplish, tasks_that_are_done):

    taskout = None
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''

            task = tasks_to_accomplish.get_nowait()
            logger.info('start processing of %s' %task['Drug'])
            m = BabelMolecule(smiles=task['Isomeric_smiles'], smilestype='iso')
            m.__call__()

            taskout = updatedrug(task, m.results)



        except queue.Empty:
            logger.info('Queue is / was empty -> exiting from worker')
            break



        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            out = (taskout, m.results, current_process().name)
            tasks_that_are_done.put(out)
            time.sleep(.05)
    return True


def listener(tasks_that_are_done)



def readspread(spreadpath):
    sp = Spreadsheet(spreadpath)
    sp.addcolumns('energypreopt')
    sp.addcolumns('minimizedenergy')
    sp.addcolumns('outputfile')
    logger.info('Spread sheet read, new columns defined and saved to object')

    return sp


def main(spreadfile=None):
    """"""
    global logger
    number_of_processes = 6
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    manager = Manager()
    q = manager.Queue()
    pool = Pool(cpu_count() -3)

    # put listener to work first
    watcher = pool.apply_async(listener, (q,))


    if spreadfile is not None:
        sp = readspread(spreadfile)
        counter = 0
        logger.info('Queuing substances from spreadsheet')
        for _, row in sp.dataframe.iterrows():
            tasks_to_accomplish.put(row)
            counter += 1
            if counter == 50:
                 break
        logger.info('Queuing substances done.')
        logger.info('There are %s ' % len(sp.dataframe.index) + 'jobs queued.')



    #creating processes
    for w in range(number_of_processes):
        p = Process(target=worker, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join(60)

    # print the output
    newdf = []
    while not tasks_that_are_done.empty():
        t = tasks_that_are_done.get()

        newdf.append(t[0])
        print(len(newdf), 'dkdkdkdk')
        t0 = t[0]['Drug']
        t1 = t[1]['error']
        t2 = t[2]

        if t1:
            logger.error('Processing of %s produced the following error(s): %s' % (t0, t1))
        else:
            logger.info('%s was successfully processed by %s' % (t0, t2))

    _nn = pd.concat(newdf, axis=1)
    nn = _nn.transpose()
    nn.to_csv('babelfromdruglist.csv')

    return tasks_to_accomplish


if __name__ == '__main__':
    # errorfix for ipython
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    #sp = readspread()

    que = main(spreadfile='druglist.xlsx')

# Leftovers

   # logger.warning('\n New run started at .....')
    # l = [{'smiles': 'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype': 'iso'},
    #      #{'smiles': 'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype': 'iso'},
    #      #{'smiles': 'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype': 'iso'},
    #       #{'smiles': 'C[C@H]1[C@H]([C@@](C[C@@H](O1)O[C@@H]2[C@H]([C@@H]([C@H](O[C@H]2OC3=C4C=C5C=C3OC6=C(C=C(C=C6)[C@H]([C@H](C(=O)N[C@H](C(=O)N[C@H]5C(=O)N[C@@H]7C8=CC(=C(C=C8)O)C9=C(C=C(C=C9O)O)[C@H](NC(=O)[C@H]([C@@H](C1=CC(=C(O4)C=C1)Cl)O)NC7=O)C(=O)O)CC(=O)N)NC(=O)[C@@H](CC(C)C)NC)O)Cl)CO)O)O)(C)N)O', 'smilestype': 'iso'},
    #      ]
    #
    #
    #
    # for i in l:
    #     logger.info('Queueing substance xyz')
    #     tasks_to_accomplish.put(i)