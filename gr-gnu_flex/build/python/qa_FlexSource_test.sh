#!/usr/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir="/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/python"
export GR_CONF_CONTROLPORT_ON=False
export PATH="/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/python":$PATH
export LD_LIBRARY_PATH="":$LD_LIBRARY_PATH
export PYTHONPATH=/mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/build/swig:$PYTHONPATH
/usr/bin/python3 /mnt/c/Users/jonny/Documents/Uni/Project/gnu-radio-implementation-for-flex/gr-gnu_flex/python/qa_FlexSource.py 
