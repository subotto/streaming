
#include <turbojpeg.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>

typedef struct {
  unsigned char *buf;
  int width, height, subsamp;
} Image;

void free_image(Image *image) {

  free(image->buf);
  free(image);

}

Image *read_frame(FILE *fin) {

  Image *image = (Image*) malloc(sizeof(Image));

  uint32_t length;
  size_t res;
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
  tjDecompress2(jpeg_dec, buf, length, image->buf, image->width, 0, image->height,  TJPF_RGBX, TJFLAG_FASTDCT);
  tjDestroy(jpeg_dec);

  free(buf);

  return image;

}

#define JPEG_QUALITY 90

void write_frame(FILE *fout, Image *image) {

  unsigned long length;
  unsigned char *buf = NULL;

  tjhandle jpeg_enc = tjInitCompress();
  tjCompress2(jpeg_enc, image->buf, image->width, 0, image->height, TJPF_RGBX, &buf, &length, TJSAMP_444, JPEG_QUALITY, TJFLAG_FASTDCT);
  tjDestroy(jpeg_enc);

  uint32_t length32 = htonl((uint32_t) length);
  size_t res;
  res = fwrite(&length32, 4, 1, fout);
  assert(res == 1);
  res = fwrite(buf, 1, length, fout);
  assert(res == length);

  tjFree(buf);

}

int main() {

  //freopen("test.stream", "r", stdin);

  while (1) {
    Image *image = read_frame(stdin);
    write_frame(stdout, image);
    free_image(image);
  }

  return 0;

}
