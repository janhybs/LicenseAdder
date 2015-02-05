import urllib2
import os
import sys
import subprocess
from subprocess import Popen, PIPE, STDOUT
import time
from optparse import OptionParser
import re


def parse () :
    parser = OptionParser ()
    parser.add_option ("-s", "--skip", dest="skip", default=False, help="skip non-existing resources",
                       action='store_true')
    parser.add_option ("-p", "--path", dest="path", default="./",
                       help="change default directory so all given relative paths will be changed",
                       metavar="FILE")
    parser.add_option ("-f", "--file", dest="files", metavar="FILENAME", default=[],
                       help="absolute or relative path to file which will be processed", action="append")
    parser.add_option ("-d", "--dir", dest="dirs", metavar="DIRECTORY", default=[],
                       help="absolute or relative path to directory which will recursively be processed",
                       action="append")
    parser.add_option ("-e", "--extension", dest="extensions", metavar="FILE_ENDING", default=[],
                       help="allowed extension for files to be processed, if empty all extensions will be processed",
                       action="append")

    parser.add_option ("-o", "--oldlicense", dest="oldlicense", default=None,
                       help="if not specified, standard /*! ... */ will be searched for in files, otherwise specify path to file, which will contain previous license text",
                       metavar="FILE")
    parser.add_option ("-n", "--newlicense", dest="newlicense", default=None,
                       help="absolute or relative path to file which contains new license", metavar="FILE")
    parser.set_usage("""%prog [options]
        Default behaviour is to search for license in files and remove it.
        If newlicense is set current license will be replaced by given newlicense.

        Note:
            1) Flags -f -d -e can be used multiple times
            2) Default license appearance is sequence starting with A and ending with B where
                A = /*!
                B = */
                that is 'C family' language comments /*! ... */
            3) Extension can also contain more than just extension, e.g. flag -e unittest.cc will match everything
                ending with sequence unittest.cc i.e.:
                    main_unittest.cc
                    fem.unittest.cc
                    unittest.cc

        Example 1:
            replace license (default license is /*! ... */) in all files in current dir and in /var/www/
            python %prog -n /home/example/license-new.txt -d ./ -d /var/www/

        Example 2:
            remove license which looks like the one in file old-license.txt from given
            files (with extension *.cc or *.c) and files in current folder (with extension *.cc or *.c)
            python %prog -d ./ -d -o old-license.txt -e .cc -e .c""")
    (options, args) = parser.parse_args ()
    return (options, args)


def normalizePaths (pathPrefix, locations) :
    normalized = [normalizePath (pathPrefix, location) for location in locations]
    return normalized


def normalizePath (pathPrefix, location) :
    if not location : return None
    return os.path.abspath (os.path.join (pathPrefix, location))


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


def handleFile (file, opts) :
    print 'doing ' + file
    content = loadTrimmed (file)
    oldlicense = opts['oldlicense']
    newlicense = opts['newlicense']
    result = None

    if isinstance (oldlicense, basestring) :
        try :
            index = content.index (oldlicense)
            rest = content[index + len (oldlicense) :]
            result = newlicense + rest
        except ValueError :
            print "license not found"
    else :
        try :
            indices = oldlicense.search (content).span ()
            rest = content[indices[1] :]
            result = newlicense + rest
        except AttributeError :
            print "license not found"
    print result



def loadLicense (oldlicense) :
    if not oldlicense :
        return None
    return open (oldlicense, "r").read ()


def handleFiles (files, opts, root="", level=1) :
    for file in files :
        realfile = os.path.join (root, file)
        print '--' * level + realfile
        # recursion for dirs
        if os.path.isdir (realfile) :
            handleFiles (os.listdir (realfile), opts, realfile, level + 1)
        else :
            # no rules or correct extension
            if not exts or checkExtension (realfile, exts) :
                handleFile (realfile, opts)
            else :
                # print ("file skipped " + file)
                pass


def loadTrimmed (file) :
    if not file :
        return None
    # return open (file, "r").read ().strip ()
    return open (file, "r").read ()


if __name__ == "__main__" :
    (options, args) = parse ()
    print (options)
    files = normalizePaths (options.path, options.files)
    dirs = normalizePaths (options.path, options.dirs)
    oldlicense = loadLicense (normalizePath (options.path, options.oldlicense))
    newlicense = loadLicense (normalizePath (options.path, options.newlicense))
    exts = options.extensions

    if oldlicense == None :
        oldlicense = re.compile ('(/\*!)(.*)(\*/)', re.M)
        oldlicense = re.compile ('\/\*!.*?(\*\/)', re.S)
    else :
        oldlicense = oldlicense.strip ()

    if newlicense :
        newlicense = newlicense.strip ()

    checkExistance (files + dirs, options.skip)
    opts = { 'exts' : exts, 'oldlicense' : oldlicense, 'newlicense' : newlicense }

    print 'solo files: '
    handleFiles (files, opts)

    print 'dirs: '
    handleFiles (dirs, opts)
