
#ifndef IMGIO_H
#define IMGIO_H

#include <stdio.h>

#include <SDL.h>

#include <cairo.h>

#include "pytj.h"

typedef struct {
  unsigned char *buf;
  unsigned char *jpeg_buf;
  int jpeg_length;
  unsigned char *yuv_buf;
  int yuv_len;
  int width, height, subsamp;
  double timestamp;
  cairo_surface_t *surf;
  cairo_t *ctx;
} Image;


Image *clone_image(const Image *image);
void free_image(Image *image);
Image *read_jpeg_frame(TJContext *ctx, FILE *fin);
Image *read_frame(TJContext *ctx, FILE *fin);
Image *read_frame_to_yuv(TJContext *ctx, FILE *fin);
int write_jpeg_frame(TJContext *ctx, FILE *fout, Image *image);
int write_frame(TJContext *ctx, FILE *fout, Image *image);
void get_cairo_context(Image *image);
void copy_yuv_to_planes(const Image *image, Uint16 *pitches, Uint8 **pixels, int swap_chroma);

#endif
