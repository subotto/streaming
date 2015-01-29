
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <cairo.h>
#include <turbojpeg.h>

typedef struct {
  unsigned char *buf;
  int width, height, subsamp;
  double timestamp;
  cairo_surface_t *surf;
  cairo_t *ctx;
} Image;

void free_image(Image *image) {

  free(image->buf);
  free(image);
  if (image->ctx) cairo_destroy(image->ctx);
  if (image->surf) cairo_surface_destroy(image->surf);

}

Image *read_frame(FILE *fin) {

  Image *image = (Image*) malloc(sizeof(Image));
  image->surf = NULL;
  image->ctx = NULL;

  uint32_t length;
  double timestamp;
  size_t res;
  res = fread(&timestamp, 8, 1, fin);
  assert(res == 1);
  res = fread(&length, 4, 1, fin);
  assert(res == 1);
  length = ntohl(length);
  //fprintf(stderr, "read length: %d\n", length);
  void *buf = malloc(length);
  res = fread(buf, 1, length, fin);
  assert(res == length);

  tjhandle jpeg_dec = tjInitDecompress();
  tjDecompressHeader2(jpeg_dec, buf, length, &image->width, &image->height, &image->subsamp);
  image->buf = malloc(image->width * image->height * 4);
  image->timestamp = timestamp;
  tjDecompress2(jpeg_dec, buf, length, image->buf, image->width, 0, image->height,  TJPF_RGBX, TJFLAG_FASTDCT);
  tjDestroy(jpeg_dec);

  free(buf);

  return image;

}

#define JPEG_QUALITY 50

void write_frame(FILE *fout, Image *image) {

  unsigned long length;
  unsigned char *buf = NULL;

  tjhandle jpeg_enc = tjInitCompress();
  tjCompress2(jpeg_enc, image->buf, image->width, 0, image->height, TJPF_RGBX, &buf, &length, TJSAMP_444, JPEG_QUALITY, TJFLAG_FASTDCT);
  tjDestroy(jpeg_enc);

  uint32_t length32 = htonl((uint32_t) length);
  size_t res;
  res = fwrite(&image->timestamp, 8, 1, fout);
  assert(res == 1);
  res = fwrite(&length32, 4, 1, fout);
  assert(res == 1);
  res = fwrite(buf, 1, length, fout);
  assert(res == length);

  tjFree(buf);

}

void setup_cairo(Image *image) {

  image->surf = cairo_image_surface_create_for_data(image->buf, CAIRO_FORMAT_RGB24, image->width, image->height, 4 * image->width);
  image->ctx = cairo_create(image->surf);

}

void edit_frame(Image *image) {

  cairo_scale(image->ctx, image->width/4, image->height/3);
  cairo_set_source_rgb(image->ctx, 0.0, 1.0, 0.0);
  cairo_select_font_face(image->ctx, "Ubuntu Medium", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL);
  cairo_set_font_size(image->ctx, 0.12);
  char *text = "MATEMATICI 1874 1110 FISICI";
  cairo_text_extents_t extents;
  cairo_text_extents(image->ctx, text, &extents);
  cairo_move_to(image->ctx, 0.1, 0.1 - extents.y_bearing);
  cairo_show_text(image->ctx, text);

  // Load reasonable matrix
  cairo_identity_matrix(image->ctx);
  double versor_len = 0.7 * image->height;
  cairo_matrix_t reflect;
  cairo_matrix_init(&reflect, 1.0, 0.0, 0.0, -1.0, 0.0, 0.0);
  cairo_transform(image->ctx, &reflect);
  cairo_translate(image->ctx, image->width/2, -image->height/2);
  cairo_scale(image->ctx, versor_len, versor_len);

  // Load reasonable default line style
  cairo_set_line_width(image->ctx, 1.5 / versor_len);
  cairo_set_line_join(image->ctx, CAIRO_LINE_JOIN_ROUND);
  cairo_set_line_cap(image->ctx, CAIRO_LINE_CAP_ROUND);

  cairo_move_to(image->ctx, 0.0, 0.0);
  cairo_line_to(image->ctx, 0.5, 0.5);
  cairo_stroke(image->ctx);

}

int main() {

  //freopen("test.stream", "r", stdin);

  while (1) {
    Image *image = read_frame(stdin);
    setup_cairo(image);
    edit_frame(image);
    cairo_surface_flush(image->surf);
    write_frame(stdout, image);
    free_image(image);
  }

  return 0;

}
