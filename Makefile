
CFLAGS = -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

all: test_filter sdl_sink _pytj.so

_pytj.o: _pytj.c _pytj.h
	gcc -c -fpic _pytj.c

_pytj_wrap.c: _pytj.i _pytj.h
	swig -python _pytj.i

_pytj_wrap.o: _pytj_wrap.c _pytj.h
	gcc -c -fpic _pytj_wrap.c `python-config --cflags`

_pytj.so:_pytj.o _pytj_wrap.o
	gcc -shared -o _pytj.so `python-config --libs` -lturbojpeg _pytj.o _pytj_wrap.o

test_filter: _pytj.c _pytj.h imgio.c imgio.h test_filter.c
	gcc -o test_filter _pytj.c imgio.c test_filter.c -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

sdl_sink: _pytj.c _pytj.h imgio.c imgio.h sdl_sink.c
	gcc -o sdl_sink _pytj.c imgio.c sdl_sink.c -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`
