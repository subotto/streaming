
CFLAGS = -lturbojpeg -g -O2 `pkg-config --cflags --libs cairo`

all: test_filter
