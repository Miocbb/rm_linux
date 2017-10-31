#!/usr/bin/python
"""
this is a script used to remove files on linux system
to a recycle bin, the similar functionality of recycle
bin in Windows system.
"""

import os
import sys
import shutil
from glob import glob
from datetime import datetime


def SigExit(*string):
    for i in string:
        print i,
    sys.exit()


def echo_help():
    """
    print help information.
    """
    print "Usage: rm [-h] [-f] f_name, ..."
    print ""
    print "Safely remove files on Linux system to recycle bin,"
    print "which is similar to windows recycle bin functionality."
    print ""
    print "Postional arguments:"
    print "{:20s}  {}".format("f_name", "target files to delete, at least one")
    print "{:20s}  {}".format("", "file name is required.")
    print "Optional arguments:"
    print "{:20s}  {}".format("-h --help", "show this help message and exit.")
    print "{:20s}  {}".format("-f", "force to delete file or dir permanently.")


def combine_string(str_list):
    rst = ""
    for i in str_list:
        rst += i+", "
    return rst.rstrip(', ')


def get_argument():
    """
    parser arguments from sys.argv.
    return (postional, optional argument).
    """
    argv = sys.argv
    argv_pst = []
    argv_opt = []
    for i in argv[1:]:
        if i.startswith('-'): argv_opt.append(i)
        else:
            argv_pst.append(i)
    return argv_pst, argv_opt


def get_parser(argv_pst, argv_opt):
    """
    parse the arguments.

    Posotional argument
    file, ...: name of the file needed removed.
               shell expression is supported.

    Optional argument
    -h: show help information.
    -f: remove file permanently.


    return list(__arg_pst), list(__arg_opt)
        1. a list of valid path in which every element will be
        moved to the recycle bin.
        2. a list of valid optional arguments.
    """
    invalid_pst = []
    __arg_pst = []
    # filter argv_pst
    for i in argv_pst:
        # os.path.expanduser will replace '~' with
        # environmental var $HOME, if '~' is leading
        # a string.
        # for usage of glob.glob:
        # https://docs.python.org/2/library/glob.html
        tem = glob(os.path.expanduser(i))
        if tem:
            __arg_pst += tem
        else:
            invalid_pst.append(i)
    if invalid_pst:
        print 'rm: file "{}" not existed.'\
        .format(combine_string(invalid_pst))

    # filter argv_opt
    reminder_opt = list(set(argv_opt)-set(['-h', '--help', '-f']))
    if reminder_opt:
        string = combine_string(reminder_opt)
        SigExit('rm: optional arguments "{}" invalid.'.format(string))
    return list(set(__arg_pst)), list(set(argv_opt)-set(['--help']))


def get_file_name(path):
    return path.split('/')[-1]


def _move(path1, path2):
    shutil.move(path1, path2)


def _delete(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        #shutil.rmtree does not work for symbolic link to a dir
    elif os.path.isfile(path):
        os.remove(path)


def write_log(path_folder, name, source, time):
    """
    write log file (.log) to the folders in recycle bin.
    for each file in the folder in recycle bin, this log
    file records its original path and time of deleted.
    """
    path_log = path_folder + '/.log'
    if not os.path.isfile(path_log):
        f = open(path_log, 'w')
        print >>f, time
        print >>f, "Log file for deleted files is created."
        print >>f, "Format of information is following:"
        print >>f, "delete time : file name : original source"
        print >>f, ""
        f.close()
    f = open(path_log, 'a')
    print >>f, "{:22} : {} : {}".format(time, name, source)
    f.close()


def main():
    arg_pst, arg_opt = get_argument()
    __arg_pst, __arg_opt = get_parser(arg_pst, arg_opt)

    # show help information
    if '-h' in __arg_opt:
        echo_help()
        sys.exit()
    if not __arg_pst:
        SigExit("rm: no valid file name.")

    # start doing rm
    # path of recycle bin
    path_recycle = os.path.expanduser('~') + '/.recycle_bin'
    time=datetime.now()
    time_str = time.strftime('%Y-%m-%d (%H:%M:%S)')
    # path of folders in recycle_bin based on year and month
    path_folder = path_recycle + '/' + str(time.year) +'_' + str(time.month)
    # time extension with ".time.day_time.hour_time_min_time.sec_time.microsec"
    exts_time = '.' + str(time.day) + '_' + str(time.hour)\
                + '_' + str(time.minute) + '_' + str(time.second)\
                + '_' + str(time.microsecond)

    if __arg_pst: # rm or mv file when file list is not empty
        if '-f' in __arg_opt: # permanently delete files
            for i in __arg_pst:
                _delete(i)
        else: # move files to recycle_bin and add time extension to files
            pwd = os.getcwd()
            if not os.path.exists(path_recycle):
                os.mkdir(path_recycle)
            if not os.path.exists(path_folder):
                os.mkdir(path_folder)
            for i in __arg_pst:
                name = get_file_name(i)
                new_name = name + exts_time
                path_new_file = path_folder + '/' + new_name
                _move(i, path_new_file)
                write_log(path_folder, new_name, os.path.abspath(i), time_str)


if __name__ == '__main__':
    main()
