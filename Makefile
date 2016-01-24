
CFLAGS = -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

all: test_filter sdl_sink _pytj.so test_client multimonitor v4l2_source

pytj.o: pytj.c pytj.h Makefile
	gcc -c -fpic pytj.c

pytj_wrap.c: pytj.i pytj.h Makefile
	swig -python pytj.i

pytj_wrap.o: pytj_wrap.c pytj.h Makefile
	gcc -c -fpic pytj_wrap.c `python2-config --cflags`

_pytj.so: pytj.o pytj_wrap.o Makefile
	gcc -shared -o _pytj.so `python2-config --libs` -lturbojpeg pytj.o pytj_wrap.o

test_filter: pytj.c pytj.h imgio.c imgio.h test_filter.c Makefile
	gcc -Wall -pedantic -o test_filter pytj.c imgio.c test_filter.c -std=c99 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

sdl_sink: pytj.c pytj.h imgio.c imgio.h sdl_sink.c Makefile
	gcc -Wall -pedantic -o sdl_sink pytj.c imgio.c sdl_sink.c -std=c99 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`

test_client: net.cpp net.hpp pytj.c pytj.h imgio.c imgio.h test_client.cpp Makefile
	g++ -Wall -pedantic -o test_client net.cpp pytj.c imgio.c test_client.cpp -std=c++11 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs` -lpthread

multimonitor: net.cpp net.hpp pytj.c pytj.h imgio.c imgio.h multimonitor.cpp Makefile
	g++ -Wall -pedantic -o multimonitor net.cpp pytj.c imgio.c multimonitor.cpp -std=c++11 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs` -lpthread

v4l2_source: v4l2_source.c imgio.c imgio.h pytj.c pytj.h Makefile
	gcc -Wall -pedantic -o v4l2_source v4l2_source.c imgio.c pytj.c -std=c11 -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo` `sdl-config --cflags --libs`
