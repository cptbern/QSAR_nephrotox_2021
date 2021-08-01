from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.six import StringIO
from rdkit.Chem.SaltRemover import SaltRemover

class RDKMolecule:
    def __init__(self, smiles='nan', smilestype=None, salts=['Ag', 'Au', 'Pt', 'Fe', 'Na', 'K', 'Cl', 'Br', 'F']):
        """"""
        self.inputerror = 0

        try:

            if str(smiles) != 'nan':
                self.mol = Chem.MolFromSmiles(smiles)


            else:
                raise AttributeError

        except AttributeError:
            self.inputerror = 1

        finally:
            removed = 0
            if salts is not None and self.inputerror != 1:
                _salts = ','.join(salts)
                _inatoms = self.mol.GetNumAtoms()
                # print(_salts)
                remover = SaltRemover(defnData="[%s]" %_salts)
                res = remover.StripMol(self.mol, dontRemoveEverything=True)
                _finatoms = res.GetNumAtoms()
                removed = _inatoms-_finatoms
                self.mol = res
                # print(Chem.MolToSmiles(self.mol))

            self.results = {'structurestring': smiles,
                            'inputerror': self.inputerror,
                            'ions_removed': removed}

            # print('removed', removed)


    def gen3d(self,):
        self.mol = Chem.AddHs(self.mol)
        AllChem.EmbedMolecule(self.mol)

    def write2string(self):
        sio = StringIO()
        w = Chem.SDWriter(sio)
        w.write(self.mol)
        w.flush()
        self.results['structurestring'] = sio.getvalue()


    def __call__(self):
        if self.inputerror == 0:
            self.gen3d()
            self.write2string()



