from unittest import TestCase
from main import LicenseManager

__author__ = 'jan-hybs'


class TestLicenseManager (TestCase) :
    def test_normalizePath (self) :

        man = LicenseManager()

        path = '/var/www/'
        file = 'file.txt'
        normPath = man.normalizePath(path, file)
        self.assertEqual(normPath, '/var/www/file.txt')

        path = '/var/www/'
        file = './file.txt'
        normPath = man.normalizePath(path, file)
        self.assertEqual(normPath, '/var/www/file.txt')


        path = '/var/www/'
        file = '.file.txt'
        normPath = man.normalizePath(path, file)
        self.assertEqual(normPath, '/var/www/.file.txt')


    def test_handleFile (self) :
        pass