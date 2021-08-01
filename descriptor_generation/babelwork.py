from openbabel import pybel
import time

class BabelMolecule:

    def __init__(self, uid=None, smiles='nan', smilestype=None, sdffile=None, mdlthree='nan', log=True):
        """mdlthree represents an 3D-mdl file in string representation"""
        # no error, 1 = Attribute Error
        self.inputerror = 0
        self.mass = 'nan'
        self._nonthree = False

        try:
            if str(smiles) != 'nan' and smilestype == 'iso' or smiles == 'can':
                self.mol = pybel.readstring('smi', smiles)

            elif sdffile is not None:
                self.mol = next(pybel.readfile('mdl', sdffile))

            elif str(mdlthree) != 'nan':
                self._nonthree = True
                self.mol = pybel.readstring('mdl', mdlthree)

            else:
                raise AttributeError

            self.mass = self.mol.molwt

        except AttributeError:
            self.inputerror = 1

        finally:
            self.energy = None

            self.results = {'uid': uid,
                            'energypreopt': 'nan',
                            'energyminimized': 'nan',
                            'inputerror' : self.inputerror,
                            'error': 'nan',
                            'molmass' : self.mass,
                            'smiles': smiles,
                            'smilestype': smilestype,
                            'sdffile': sdffile,
                            'structurestring': 'nan',
                            }

            if log is not False:
               self.protocol()

    def gen3d(self, forcefield='uff', steps=500):
        """Generate 3D structure with given forcefield and amount of refining steps.
        Hydrogens are added directly"""
        self.mol.make3D(forcefield, steps)

    def minimize(self, forcefield='mmff94', steps=5000):
        """Minimize molecule energy. Carefull, routine does not add hydrogens automatically. The SteepestDescent
        algorithm is used by default. For more detail: https://github.com/openbabel/documentation/blob/master/pybel.py line 318-403"""
        self.mol.localopt(forcefield, steps)

    def getengery(self, forcefield='mmff94'):
        ff = pybel._forcefields[forcefield]
        if ff.Setup(self.mol.OBMol) is not False:
            self.energy = ff.Energy()



    def converttype(self, type='mdl', overwrite=False):
        if not overwrite:
            return self.mol.write(type)
        else:
            tmpstr = self.mol.write(type)
            self.mol = pybel.readstring(type, tmpstr)
            return tmpstr

    def protocol(self):
        # self.messhand = pybel.ob.OBMessageHandler()
        # self.messhand.SetOutputLevel(1)
        # self.messhand.StartLogging()
        self.errhand = pybel.ob.obErrorLog
        self.errhand.SetOutputLevel(0)
        self.errhand.StartLogging()

    def __call__(self):
        """Routine to run calculation"""


        if self.inputerror == 0 and self._nonthree is False:
            #self.converttype(type='sdf', overwrite=True)
            self.gen3d()


        if self.inputerror !=1:
            self.getengery()
            self.results['energypreopt'] = self.energy
            self.minimize()
            self.getengery()
            self.results['energyminimized'] = self.energy
            err2 = '\n'.join(self.errhand.GetMessagesOfLevel(1))
            err1 = '%s' %time.time()
            l = [err1, err2]
            self.results['error'] = err2
            self.results['structurestring'] = self.converttype()


        self.errhand.StopLogging()
        self.errhand.ClearLog()

        del self.errhand

        return

