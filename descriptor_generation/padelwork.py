from padelpy import padeldescriptor
import os
import tempfile
import pandas as pd

class PadelMolecule():

    def __init__(self, mdlfile='nan', mdlstring='nan'):

        self._delfiles = []
        if mdlfile is not 'nan':
            if os.path.isfile(mdlfile):
                self.mdl = mdlfile
            else:
                raise FileNotFoundError

        elif mdlstring is not 'nan':
            # https://stackoverflow.com/questions/8577137/how-can-i-create-a-tmp-file-in-python/8577225
            fd, self.mdl = tempfile.mkstemp(suffix='.mdl')
            self._delfiles.append(self.mdl)
            try:
                with os.fdopen(fd, 'w') as tmp:
                    tmp.write(mdlstring)
                    tmp.close()
            except:
                pass

        else:
            raise Exception

    def setoutfile(self):
        _, outfile = tempfile.mkstemp(suffix='.csv')
        self._delfiles.append(outfile)
        return outfile

    def topandas(self, csv):
        return pd.read_csv(csv, na_values=['nan'])

    def __call__(self,):
        outcsv = self.setoutfile()
        padeldescriptor(mol_dir=self.mdl, d_2d=True, d_3d=True, d_file=outcsv, maxcpdperfile=1, maxruntime=100000)
        pan = self.topandas(outcsv)
        print(pan.head())
        for f in self._delfiles:
            os.remove(f)

        return pan.squeeze()
        #return pan