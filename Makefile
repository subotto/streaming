
CFLAGS = -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo`

all: test_filter _pytj.so

_pytj.o: _pytj.c _pytj.h
	gcc -c -fpic _pytj.c

_pytj_wrap.c: _pytj.i _pytj.h
	swig -python _pytj.i

_pytj_wrap.o: _pytj_wrap.c _pytj.h
	gcc -c -fpic _pytj_wrap.c `python-config --cflags`

_pytj.so:_pytj.o _pytj_wrap.o
	gcc -shared _pytj.o _pytj_wrap.o -o _pytj.so `python-config --libs` -lturbojpeg
