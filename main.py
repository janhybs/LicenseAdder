import urllib2
import os
import sys
import subprocess
from subprocess import Popen, PIPE, STDOUT
import time
from optparse import OptionParser


def parse () :
    parser = OptionParser ()
    parser.add_option ("-s", "--skip", dest="skip", default=False, help="skip non-existing resources",
                       action='store_true')
    parser.add_option ("-p", "--path", dest="path", default="./", help="xml location, default current directory",
                       metavar="FILE")
    parser.add_option ("-f", "--file", dest="files", metavar="FILENAME", default=[], help="", action="append")
    parser.add_option ("-d", "--dir", dest="dirs", metavar="DIRECTORY", default=[], help="", action="append")
    parser.add_option ("-e", "--extension", dest="extensions", metavar="EXTENSION", default=[], help="",
                       action="append")

    parser.add_option ("-o", "--oldlicense", dest="oldlicense", default=None, help="", metavar="FILE")
    parser.add_option ("-n", "--newlicense", dest="newlicense", default=None, help="", metavar="FILE")

    (options, args) = parser.parse_args ()
    return (options, args)


def normalizePath (pathPrefix, locations) :
    normalized = [os.path.abspath (os.path.join (pathPrefix, location)) for location in locations]
    return normalized


def checkExistance (locations, skipError=True) :
    errors = []
    for location in locations :
        if not os.path.exists (location) :
            errors.append (location)

    if errors :
        if skipError :
            print ('Warning: Non existing resources: \n' + '\n'.join (errors))
        else :
            raise IOError ('Non existing resources: \n' + '\n'.join (errors))


def checkExtension (file, exts) :
    file = file.upper ()
    for ext in exts :
        if file.endswith (ext.upper ()) :
            return True
    return False


def handleFile (file, oldlicense, newlicense) :
    print 'doing ' + file
    content = loadTrimmed (file)
    try :
        index = content.index (oldlicense)
        rest = content[index + len (oldlicense) :]
        print "'"+newlicense+"'" + "'"+rest+"'"
    except ValueError :
        print "license not found"


def loadLicense (oldlicense) :
    if not oldlicense :
        return None
    return open (oldlicense, "r").read ()

def loadTrimmed (file):
    if not file :
        return None
    return open (file, "r").read ().strip ()

if __name__ == "__main__" :
    (options, args) = parse ()
    print (options)
    files = normalizePath (options.path, options.files)
    dirs = normalizePath (options.path, options.dirs)
    oldlicense = loadLicense (options.oldlicense).strip ()
    newlicense = loadLicense (options.newlicense).strip ()
    exts = options.extensions

    checkExistance (files + dirs, options.skip)

    for file in files :
        # no rules or correct extension
        if not exts or checkExtension (file, exts) :
            handleFile (file, oldlicense, newlicense)
        else :
            print ("file skipped " + file)


