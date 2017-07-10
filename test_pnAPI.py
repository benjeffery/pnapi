from unittest import TestCase
from pnapi import PnAPI


class TestPnAPI(TestCase):
    def setUp(self):
        self.api = PnAPI('Pf60_Internal', 'USER', 'PASS')

    def test__getconfig(self):
        self.api._getconfig()

    def test_avaliableProperties(self):
        print(self.api.avaliableProperties())

    def test_avaliable2DProperties(self):
        print(self.api.avaliable2DProperties())