%module pytj

%include "cdata.i"
%include </usr/include/turbojpeg.h>

%{

#include "_pytj.h"

%}

%thread;
%include "_pytj.h"
%nothread;

