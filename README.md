## Introduction

This is a script used to remove files on linux system to a recycle bin, the similar functionality of recycle bin in Windows system.

### Description:

1. A recycle bin named `.recycle_bin` will be created under your home path.
2. The time when you deleted your file will be recorded. According to the recorded time, all the deleted files will be categorized into different folders under `~/.rycycle_bin`. The name of folders in `~/.recycle_bin` is named by the year and the month according to recorded time.
3. Files thrown into the recycle_bin will be stamped by an prefix, `day_hour_minute_second_microsecond:` created by the recorded time.
4. A log file, `.log`, will be created in each folder under `~/.recycle_bin` to record the detailed information. Log file will be updated everytime when files are moved in.

## Install

1. git clone this project into a place you like, and navigate to the root of this project.
2. make `run.py` executable by run `chmod +x run.py`
3. create an alias for the execute path of `run.py`. `rm` alias is suggested for this script, so that original `rm` of linux can be overwrited.

## Usage

1. Absolute and relative path of files or directories are supported. "*" expression is also supported for specifying a class of files which match with certain pattern.
2. The usage of optional arguments is the same as linux `rm` command. The position of optional arguments can be any position after `rm` command. Combination optional arguments are supported. To pemanently delete files, use `-f` flag.  To recursively delete directories, use `-r` flag.
   **Example**:
   ```shell
   $:rm [-f, -fr, -rf] Files Dirs  # pemanently delete dirs and/or files.
   ```
   If `-f` not specified, the files will be moved to `~/.recycle_bin`, instead of deleted.
   **Example**:
   ```shell
   $:rm [-r] Files Dirs    # temporary remove files or dirs into ~/.recycle_bin.
   ```
3. To clean and delete files or directories existed inside `~/.recycle_bin`, you can ahcieve by either specifying `-f` flag or not.
   ```shell
   $:rm -f ~/.recycle_bin/files
   $:rm -f -r ~/.recycle_bin/dirs
   ```
   or just
   ```
   $:rm  ~/.recycle_bin/files
   $:rm  -r ~/.recycle_bin/dirs
   ```
   The `~/.recycle_bin/Date_Folder/.log` file will be updated after your cleaning.
