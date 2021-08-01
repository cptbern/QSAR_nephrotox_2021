from multiprocessing import Lock, Process, Queue, current_process
import threading
import time
import queue # imported for using queue.Empty exception
from babelwork import BabelMolecule
from rdkitwork import RDKMolecule
from padelwork import PadelMolecule

import logging
from sanbase.filework.spreadsheet import Spreadsheet
import pandas as pd
import copy

starttime = time.time()
logger = logging.getLogger("Pipeline")

logging.basicConfig(level=logging.INFO)

#Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

#Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)


#Add handlers to the logger
#logger.addHandler(c_handler)
#logger.addHandler(f_handler)

CSVINTERVAL = 30
TIMEOUT = 300
NUMBER_OF_PROCESSES = 8


# enables break of looping through compounds
TESTLOOP = False
TESTLOOPNB = 50


_FINISH = False


#### HELPER FUNCTIONS ####

def _updatedrug(pandas, calcs):
    """The pandas series contains all information for a drug. The contlist defines entries from the babel calculation, which
    will be added to the pandas series."""
    contlist = ['molmass', 'energypreopt', 'energyminimized', 'inputerror', 'error', 'structurestring', '3Dmethod', ]
    for ct in contlist:
        pandas[ct] = calcs[ct]

    return pandas

def _userdk4structure(smiles):
    """Uses rdkit to calculate the 3D structure in a standard mode. For details see rdk"""
    rdk = RDKMolecule(smiles)
    rdk()
    return rdk.results


def _threadrdkbabel(pandaobjs):
    rdkstructure = _userdk4structure(pandaobjs['Isomeric_smiles'])

    x = BabelMolecule(mdlthree=rdkstructure['structurestring'], log=True)
    x()

    results = x.results
    results['exitcode'] = 3
    results['3Dmethod'] = 'rdkit-babel'
    del x
    return results



def _threadbabel(pandaobjs):
    x = BabelMolecule(smiles=pandaobjs['Isomeric_smiles'], smilestype='iso')
    x()

    results = x.results
    results['exitcode'] = 3
    results['3Dmethod'] = 'babel'
    del x
    return results


def _runpadel(pandaobj):
    p = PadelMolecule(mdlstring=pandaobj['structurestring'])
    padel = p()
    x = pd.concat([pandaobj, padel])
    return x

def worker(tasks_to_accomplish, tasks_that_are_done, ):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            exitcode = 3
            start = time.time()
            task = tasks_to_accomplish.get_nowait()
            proctype = task[0]
            pandaobjs = task[1]
            logger.info('==============================================================================')
            logger.info('start processing of %s ' % task[1]['Drug'] + 'with %s' %proctype)

            results = {}

            if proctype == 'rdkitbabel':
                results = _threadrdkbabel(pandaobjs)

            elif proctype == 'babel':
                results = _threadbabel(pandaobjs)

            else:
                pass

            withstruct = _updatedrug(pandaobjs, results)

            ### run padel
            withdescriptors = _runpadel(withstruct)


            out = (withdescriptors, exitcode, current_process().name)
            tasks_that_are_done.put(out)

            while time.time() - start <= TIMEOUT:
                exitcode = 0
                end = time.time()
                logger.info('Processing of %s done. Runtime: %s' % (pandaobjs['Drug'], runtime(start, end)))
                logger.info('==============================================================================')
                break
            else:
                exitcode = 1
                end = time.time()
                logger.warning('timeout for processing of %s reached' % pandaobjs['Drug'])

        except queue.Empty:
            logger.info('Queue is / was empty -> exiting from worker')
            break

        except Exception:
            logger.info('Error .....')


        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''

            time.sleep(.05)



    return True



def listener(tasks_that_are_done,):

    newdf = []
    tCurrent = time.time()
    df = pd.DataFrame()
    while not _FINISH:
        try:
            t = tasks_that_are_done.get_nowait()
            newdf.append(t[0])
        except:
            time.sleep(5)
        time.sleep(0.225)
        if time.time() >= tCurrent + CSVINTERVAL and len(newdf) > 0:
            dfstack = pd.concat(newdf, axis=1).transpose()
            df = df.append(dfstack)
            df.to_csv('babelfromdruglist.csv')
            newdf = []
            tCurrent = time.time()


def readspread(spreadpath):
    sp = Spreadsheet(spreadpath, sheet='Sheet1')
    sp.addcolumns('3Dmethod')
    return sp

def runtime(starttime, endtime):
    return time.strftime('%H:%M:%S', time.gmtime(endtime - starttime))

def waitlistener():
    if CSVINTERVAL >= TIMEOUT:
        return CSVINTERVAL
    else:
        return TIMEOUT

def main(spreadfile=None):
    """"""
    global logger
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    logger.info('Start openbabel processing')

    if spreadfile is not None:
        sp = readspread(spreadfile)
        counter = 0
        logger.info('Queuing substances from spreadsheet')
        # As the same row is added twice to the taskqueue. Once for rdkitbabel and once for babel processing
        factor = 2
        for _, row in sp.dataframe.iterrows():
            tasks_to_accomplish.put(('rdkitbabel', row))
            #tasks_to_accomplish.put(('babel', row))
            counter += 1
            if counter == TESTLOOPNB and TESTLOOP is True:
                break
        logger.info('Queuing substances done.')
        logger.info('There are %s ' % int(len(sp.dataframe.index)*factor) + 'jobs queued.')

    global _FINISH

    #creating processes
    for w in range(NUMBER_OF_PROCESSES):
        p = Process(target=worker, args=(tasks_to_accomplish, tasks_that_are_done, ))
        processes.append(p)
        p.start()

    cl  # CWYxp*4IO
    l = Process(target=listener, args=(tasks_that_are_done,))
    l.daemon = True
    l.start()

    for p in processes:
        p.join()

    l.join()


    time.sleep(2 * waitlistener())
    _FINISH = True

    endtime = time.time()

    logger.info('==================================')
    logger.info('Processing finished, after %s' %(runtime(starttime, endtime)))
    logger.info('==================================')

    return tasks_to_accomplish


if __name__ == '__main__':
    # errorfix for ipython
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    que = main(spreadfile='druglist_learn.xlsx')


# https://stackoverflow.com/questions/13446445/python-multiprocessing-safely-writing-to-a-file