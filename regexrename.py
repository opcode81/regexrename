#!/usr/bin/python
# -*- coding: utf-8

from __future__ import print_function
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

print("\nRegExRename (C) by Dominik Jain\n")

def exitWithHelp(exitCode=0):
    print(" usage: regexrename [options] <mask> [pattern|option] ...\n")
    print("  mask:     mask with which to filter (may contain the wildcards *,?)")
    print("  options:  -p,-preview      preview only, no renames take place")
    print("            -c,-caps         capitalize all words")
    print("            -t,-title        capitalize all words as in titles")
    print("            -ix,-ignoreext   ignore file extension")
    print("            -r,-recurse      recurse subdirectories")
    print("            -sa,-showall     show all matched files, even if not renamed")
    print("            -f               process files only, skip directories")
    print("  patterns: an arbitrary number of regex patterns can be specified")
    print("            pattern format: \"old:new\"")
    print("               old: regular expression to search for")
    print("               new: replacement")
    print("                    $dir is replaced by the name of the dir the file is in")
    print("                    $idx2 is replaced with the 0-padded (two-digit) index of the file in its folder")
    print("            syntax: http://docs.python.org/lib/re-syntax.html")
    print("            groups can be referenced with \\number, starting with 1, e.g.")
    print("            \"s\\d\\de(\\d\\d):episode \\1\" will replace 's01e02' with 'episode 02'")
    print("  capitalization takes place after pattern replacement")
    print('  regexrename can be used to move files by prepending a path, e.g. "\A:../"')
    exit(exitCode)

argv = argv[1:]
if len(argv) < 2:
    exitWithHelp()

preview = False
caps = False
title = False
recurse = False
showAll = False
ignoreExt = False
filesOnly = False
patterns = []
filemask = None
for i, arg in enumerate(argv):
    if ":" in arg:
        patterns.append(arg)
    elif arg[:1] == "-":
        if arg in ("-preview", "-p"):
            preview = True
        elif arg in ("-caps", "-c"):
            caps = True
        elif arg in ("-title", "-t"):
            title = True
        elif arg in ("-recurse", "-r"):
            recurse = True
        elif arg in ("-showall", "-sa"):
            showAll = True
        elif arg in ("-ix", "-ignoreext"):
            ignoreExt = True
        elif arg in ("-f", ):
            filesOnly = True
        else:
            print("ERROR: unknown switch '%s'\n\n", arg)
            exitWithHelp(1)
    else:
        if len(patterns) > 0:
            print("ERROR: invalid argument sequence starting at %s\n\n" % str(argv[i:]))
            exitWithHelp(1)
        filemask = arg
if filemask is None:
    print("ERROR: no filemask specified\n\n")
    exitWithHelp(1)

patterns = [p.split(":") for p in patterns]

def doReplace(filename, dirpath, idxInFolder):
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
    new_filename = new_filename.replace("$idx2", "%02d" % idxInFolder)
    
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
        print("In %s:\n   %s" % (abspath, filename))
        if rename: print(" > %s\n" % new_filename)
        else: print()
    if rename and not preview:
        os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, new_filename))

if recurse:
    for dirpath, dirnames, filenames in os.walk("."):
        for idx, filename in enumerate(filenames if filesOnly else filenames + dirnames, start=1):
            if fnmatch(filename, filemask):
                doReplace(filename, dirpath, idx)
else:    
    for idx, filename in enumerate(os.listdir("."), start=1):
        if filesOnly and os.path.isdir(filename): continue
        if fnmatch(filename, filemask):
            doReplace(filename, ".", idx)
 
if preview:
    print("PREVIEW only. No files were renamed.")