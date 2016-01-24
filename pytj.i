%module pytj

%include "cdata.i"
%include </usr/include/turbojpeg.h>

%{

#include "pytj.h"

%}

%thread;
%include "pytj.h"
%nothread;

