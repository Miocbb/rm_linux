#!/usr/bin/python
"""
this is a script used to remove files on linux system
to a recycle bin, the similar functionality of recycle
bin in Windows system.
"""

import os
import sys
import shutil
import subprocess
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
    print "Usage: rm [-h] [-f] [-r] files, dirs ..."
    print ""
    print "Safely remove files on Linux system to recycle bin,"
    print "which is similar to windows recycle bin functionality."
    print ""
    print "Postional arguments:"
    print "{:20s}  {}".format("f_name", "target files to delete, at least one")
    print "{:20s}  {}".format("", "file name is required.")
    print "Optional arguments:"
    print "{:20s}  {}".format("-h --help", "show this help message and exit.")
    print "{:20s}  {}".format("-f", "force to delete file or directory permanently.")
    print "{:20s}  {}".format("-r", "recursively remove directory.")

def combine_string(str_list):
    rst = ""
    for i in str_list:
        rst += i+", "
    return rst.rstrip(', ')

def get_file_name(path):
    return path.split('/')[-1]

def get_file_mount_name(path):
    path = os.path.abspath(os.path.expanduser(path))
    cmd_df = ['df', '-P', '-T', path]
    cmd_tail = ['tail', '-n', '+2']
    p1 = subprocess.Popen(cmd_df, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_tail, stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output= p2.communicate()[0]
    rst = output.split()[-1]
    if rst != '/':
        rst = rst.rstrip('/')
    return rst

def check_if_mounted_file(path):
    return get_file_mount_name(path) != '/'

def _move(path1, path2):
    shutil.move(path1, path2)

def _delete(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        #shutil.rmtree does not work for symbolic link to a dir
    elif os.path.isfile(path):
        os.remove(path)

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
    -r: recursively remove directory.
    -rf, -fr: supported.
    
    Note: recursively remove opt argument ('-r') is acceptable and will not
    raise error, but it will be ignored since files and directorise
    are treated equally in this program.

    return list(__arg_pst), list(__arg_opt)
        1. a list of valid path in which every element will be
        moved to the recycle bin.
        2. a list of valid optional arguments.
    """
    # individual acceptable optional arguments.
    # add two dummy opt arguments ('-rf', '-fr') to be compatible with
    # linux "rm -rf".
    valid_opt = ('-h', '--help', '-r', '-f', '-rf', '-fr')
    invalid_pst = []
    __arg_pst = []
    __arg_opt = []
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
        print 'safe_rm: file "{}" not existed.'\
        .format(combine_string(invalid_pst))
    __arg_pst = list(set(__arg_pst))

    # deal with '-r' contained opt args.
    if set(argv_opt) & set(['-rf', '-fr']):
        argv_opt.extend(['-f', '-r'])
    # filter argv_opt
    reminder_opt = list(set(argv_opt) - set(valid_opt))
    if reminder_opt:
        string = combine_string(reminder_opt)
        SigExit('safe_rm: optional arguments "{}" invalid.'.format(string))
    __arg_opt = list(set(argv_opt) - set(['--help']))
    return __arg_pst, __arg_opt

def write_log(path_folder, name, source, time):
    """
    write log file (.log) to the folders in recycle bin.
    for each file in the folder in recycle bin, this log
    file records its original path and time of deleted.
    """
    path_log = path_folder + '/.log'
    if check_if_mounted_file(source):
        source = source[len(get_file_mount_name(source)):]
        source = '~' + source
    if not os.path.isfile(path_log):
        f = open(path_log, 'w')
        print >>f, time
        print >>f, "Log file for deleted files is created."
        print >>f, "Format of information is following:"
        print >>f, "delete time : file name : original source"
        print >>f, ""
        f.close()
    f = open(path_log, 'a')
    print >>f, "{:22}   {}   {}".format(time, name, source)
    f.close()

def update_log(path_file):
    """
    update the log file in ~/.recycle_bin/Date_Folder/.log
    when the user is cleanning the recycle bin.

    delete the record information in log file when the file
    is cleaned out from recycle bin.
    """
    file_name = get_file_name(path_file)
    # remove .log file, no need to update log file
    if file_name == '.log':
        return
    log_name  = path_file.rstrip(file_name) + '.log'
    # update .log when user is cleanning content
    # in the ~/.recycle_bin/Date_Folder/
    if os.path.isfile(log_name):
        f = open(log_name, 'r+')
        f_content = f.readlines()
        f.seek(0)
        del_line = [line for line in f if file_name in line ]
        f.seek(0)
        for line in f_content:
            if line not in del_line:
                f.write(line)
        f.truncate()
        f.close

def main():
    arg_pst, arg_opt = get_argument()
    __arg_pst, __arg_opt = get_parser(arg_pst, arg_opt)

    # show help information
    if '-h' in __arg_opt:
        echo_help()
        sys.exit()
    if not __arg_pst:
        SigExit("safe_rm: no valid file name.")

    # start doing rm
    # abs_path of recycle bin
    path_recycle = os.path.expanduser('~') + '/.recycle_bin'
    time=datetime.now()
    time_str = time.strftime('%Y-%m-%d(%H:%M:%S)')
    # abs_path of folders in recycle_bin based on year and month
    path_folder = path_recycle + '/' + str(time.year) +'_' + str(time.month)
    # time extension with ".time.day_time.hour_time_min_time.sec_time.microsec"
    exts_time = str(time.day) + '_' + str(time.hour)\
                + '_' + str(time.minute) + '_' + str(time.second)\
                + '_' + str(time.microsecond)

    if __arg_pst: # start rm or mv file
        if '-f' in __arg_opt: # permanently delete any files
            for i in __arg_pst:
                if os.path.isdir(i): # skip a dir if -r not specified.
                    if '-r' not in __arg_opt:
                        dir_n = os.path.relpath(i)
                        print "safe_rm: cannot rm: {}, {} is a directory."\
                                .format(dir_n, dir_n)
                        continue
                _delete(i)
                # update .log file if deleted file is inside ~/.recycle_bin/
                i_abs_path_file = os.path.abspath(os.path.expanduser(i))
                if i_abs_path_file.startswith(path_recycle+'/'):
                    update_log(i_abs_path_file)
        else: # move files to recycle_bin and add time extension to files
            for i in __arg_pst:
                # check if this file is mounted from remote.
                if check_if_mounted_file(i):
                    path_recycle = get_file_mount_name(i) + '/.recycle_bin'
                    path_folder = path_recycle + '/' + str(time.year) +'_' + str(time.month)
                if not os.path.exists(path_recycle):
                    os.mkdir(path_recycle)
                if not os.path.exists(path_folder):
                    os.mkdir(path_folder)
                i_abs_path_file = os.path.abspath(os.path.expanduser(i))
                if i_abs_path_file == path_recycle:
                    SigExit("safe_rm: terminated.\n"
                            "Recycle bin is proteced. Use 'rm -rf' to delete")
                # clean recycle bin
                # rm file which is in the recycle bin already
                if i_abs_path_file.startswith(path_recycle+'/'):
                    if os.path.isdir(i): # skip a dir in recycle bin if -r not used.
                        if '-r' not in __arg_opt:
                            dir_n = os.path.relpath(i)
                            print "safe_rm: cannot rm: {}, {} is a directory."\
                                    .format(dir_n, dir_n)
                            continue
                    if get_file_name(i_abs_path_file) == '.log':
                        print "safe_rm: cannot rm log file in the trash can."
                        continue
                    _delete(i)
                    update_log(i_abs_path_file)
                else: # temporaly rm file
                    if os.path.isdir(i): # skip a dir in recycle bin if -r not used.
                        if '-r' not in __arg_opt:
                            dir_n = os.path.relpath(i)
                            print "safe_rm: cannot rm: {}, {} is a directory."\
                                    .format(dir_n, dir_n)
                            continue
                    name = get_file_name(i)
                    new_name = exts_time + ":" + name
                    path_new_file = path_folder + '/' + new_name
                    write_log(path_folder, new_name, i_abs_path_file, time_str)
                    _move(i, path_new_file)

if __name__ == '__main__':
    main()
