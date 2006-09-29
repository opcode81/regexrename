#!/usr/bin/python
# -*- coding: utf-8

import re
import os
from sys import argv, exit
from fnmatch import fnmatch

def capitalizeMatch(match):
    word = match.group(0)
    if not word.lower() in ["of", "the", "to", "for", "a", "an", "in", "on", "at", "from", "with", "over", "under", "that", "it", "and", "or"]:
        if word[0].isupper():
            return word
        else:
            return word.capitalize()
    else:
        return word.lower()

def capFirstChar(s):
    return s[0].upper() + s[1:]

def titleCaps(s):    
    return " - ".join(map(lambda item: capFirstChar(re.sub('[0-9a-zA-ZäöüÄÖÜßéèáà\']+', capitalizeMatch, item)), s.split(" - ")))    

print "\nRegExRename (C) by Dominik Jain\n"
if len(argv) <= 2:
    print "%d" % len(argv), argv
    print " usage: regexrename [options] <mask> <pattern1> [pattern2] ...\n"
    print "  mask:     mask with which to filter (may contain the wildcards *,?)"
    print "  options:  -p,-preview      preview only, no renames take place"
    print "            -c,-caps         capitalize all words"
    print "            -t,-title        capitalize all words as in titles"
    print "            -ix,-ignoreext   ignore file extension"
    print "            -r,-recurse      recurse subdirectories"
    print "            -sa,-showall     show all matched files, even if not renamed"
    print "            -f               process files only, skip directories"
    print "  patterns: an arbitrary number of regex patterns can be specified"
    print "            pattern format: \"old:new\""
    print "               old: regular expression to search for"
    print "               new: replacement"
    print "                    $dir is replaced by the name of the dir the file is in"
    print "            syntax: http://docs.python.org/lib/re-syntax.html"
    print "            groups can be referenced with \\number, starting with 1, e.g."
    print "            \"s\\d\\de(\\d\\d):episode \\1\" will replace 's01e02' with 'episode 02'"
    print "  capitalization takes place after pattern replacement"
    print '  regexrename can be used to move files by prepending a path, e.g. "\A:../"'
    exit(0)

preview = False
caps = False
title = False
recurse = False
showAll = False
ignoreExt = False
filesOnly = False
for i in range(1, len(argv)):
    if not(argv[i][0] == '-'):
        break
    if argv[i] in ("-preview", "-p"):
        preview = True
    elif argv[i] in ("-caps", "-c"):
        caps = True
    elif argv[i] in ("-title", "-t"):
        title = True
    elif argv[i] in ("-recurse", "-r"):
        recurse = True
    elif argv[i] in ("-showall", "-sa"):
        showAll = True
    elif argv[i] in ("-ix", "-ignoreext"):
        ignoreExt = True
    elif argv[i] in ("-f", ):
        filesOnly = True
    else:
        print "unknown switch:", argv[i]
        exit(1)
filemask = argv[i]
patterns = []
for j in range(i+1, len(argv)):
    p = argv[j].split(":")
    if len(p) != 2:
        raise Exception("Not a valid pattern: %s" % str(p))
    patterns.append(p)

def doReplace(filename, dirpath):
    abspath = os.path.abspath(dirpath)
    dirname = os.path.split(abspath)[1]
    
    extension = ""
    new_filename = filename
    
    if ignoreExt:
        extpos = filename.rfind(".")
        if extpos != -1:
            extension = filename[extpos:]
            new_filename = filename[:extpos]
    
    # apply patterns
    for pattern in patterns:
        new_filename = re.sub(pattern[0], pattern[1], new_filename)
    new_filename = new_filename.replace("$dir", dirname)
    
    # capitalization
    if caps:
        new_filename = new_filename.title()
    if title:
        extpos = new_filename.rfind(".")
        if extpos == -1:                
            extpos = len(new_filename)
        ext = new_filename[extpos:]
        new_filename = (titleCaps(new_filename[:extpos]) + ext)
    
    new_filename += extension
    
    rename = new_filename != filename
    if rename or showAll:
        print "In %s:\n   %s" % (abspath, filename)
        if rename: print " > %s\n" % new_filename
        else: print    
    if rename and not preview:
        os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, new_filename))

if recurse:
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames if filesOnly else filenames + dirnames:
            if fnmatch(filename, filemask):
                doReplace(filename, dirpath)
else:    
    for filename in os.listdir("."):
        if filesOnly and os.path.isdir(filename): continue
        if fnmatch(filename, filemask):
            doReplace(filename, ".")
 