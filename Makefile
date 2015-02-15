
CFLAGS = -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

all: test_filter sdl_sink _pytj.so test_client

_pytj.o: _pytj.c _pytj.h Makefile
	gcc -c -fpic _pytj.c

_pytj_wrap.c: _pytj.i _pytj.h Makefile
	swig -python _pytj.i

_pytj_wrap.o: _pytj_wrap.c _pytj.h Makefile
	gcc -c -fpic _pytj_wrap.c `python-config --cflags`

_pytj.so:_pytj.o _pytj_wrap.o Makefile
	gcc -shared -o _pytj.so `python-config --libs` -lturbojpeg _pytj.o _pytj_wrap.o

test_filter: _pytj.c _pytj.h imgio.c imgio.h test_filter.c Makefile
	gcc -Wall -pedantic -o test_filter _pytj.c imgio.c test_filter.c -std=c99 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

sdl_sink: _pytj.c _pytj.h imgio.c imgio.h sdl_sink.c Makefile
	gcc -Wall -pedantic -o sdl_sink _pytj.c imgio.c sdl_sink.c -std=c99 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

test_client: net.cpp net.hpp _pytj.c _pytj.h imgio.c imgio.h test_client.cpp Makefile
	g++ -Wall -pedantic -o test_client net.cpp _pytj.c imgio.c test_client.cpp -std=c++11 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs` -lpthread
