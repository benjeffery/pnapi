from unittest import TestCase
from pnapi.api import PnAPI


class TestPnAPI(TestCase):
    def setUp(self):
        self.api = PnAPI('Pf60_Internal', 'USER', 'PASS')

    def test__getconfig(self):
        self.api._getconfig()

    def test_avaliableProperties(self):
        print(self.api.avaliableProperties())

    def test_avaliable2DProperties(self):
        print(self.api.avaliable2DProperties())

    def test_get2D(self):
        print(self.api.get2D('genotypes', ['calldata/genotype', 'calldata/AD'], ['POS'], ['Sample'],
                             '{"whcClass":"compound","isCompound":true,"isRoot":true,"Components":[{"whcClass":"comparefixed","isCompound":false,"ColName":"POS","CompValue":1000,"Tpe":"<"},{"whcClass":"comparefixed","isCompound":false,"ColName":"CHROM","CompValue":"Pf3D7_01_v3","ColName2":"AutoKey","Tpe":"="}],"Tpe":"AND"}',
                             None, 'POS', 'Sample'))

    def test_getGene(self):
        print(self.api.getGene('PF3D7_0709000'))

    def test_getPropsForGene(self):
        print(self.api.getPropsForGene('PF3D7_0709000', 'variants', ['POS', 'DP']))