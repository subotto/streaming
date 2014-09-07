
#include <stdlib.h>
#include <turbojpeg.h>

#include "_pytj.h"

TJContext *create_tjcontext(void) {

  TJContext *ctx = malloc(sizeof(TJContext));
  ctx->tj_enc = tjInitCompress();
  ctx->tj_dec = tjInitDecompress();

  return ctx;

}

void free_tjcontext(TJContext *ctx) {

  tjDestroy(ctx->tj_enc);
  tjDestroy(ctx->tj_dec);
  free(ctx);

}

// The buffer is assumed to be width * height * 4 (with channels RGBX)
void *encode_image(TJContext *ctx, void *buf, unsigned int width, unsigned int height, unsigned int *res_len, int quality) {

  unsigned long length;
  unsigned char *outbuf = NULL;

  tjCompress2(ctx->tj_enc, buf, width, 0, height, TJPF_RGBX, &outbuf, &length, TJSAMP_444, quality, TJFLAG_FASTDCT);
  *res_len = length;

  return outbuf;

  tjFree(buf);

}

void free_encoded_image(void *buf) {

  tjFree(buf);

}

void *decode_image(TJContext *ctx, void *buf, unsigned long len, unsigned int *res_width, unsigned int *res_height) {

  int width;
  int height;
  int subsamp;
  unsigned char *outbuf;

  tjDecompressHeader2(ctx->tj_dec, buf, len, &width, &height, &subsamp);
  outbuf = malloc(width * height * 4);
  tjDecompress2(ctx->tj_dec, buf, len, outbuf, width, 0, height,  TJPF_RGBX, TJFLAG_FASTDCT);
  *res_width = width;
  *res_height = height;

  return outbuf;

}

void free_decoded_image(void *buf) {

  free(buf);

}
