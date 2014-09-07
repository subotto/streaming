
#include <stdlib.h>
#include <strings.h>
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
EncodeRes encode_image(TJContext *ctx, unsigned long _buf, unsigned int width, unsigned int height, int quality) {

  unsigned long length;
  unsigned char *buf = (unsigned char*) _buf;
  unsigned char *outbuf = NULL;

  EncodeRes res;
  bzero(&res, sizeof(EncodeRes));

  tjCompress2(ctx->tj_enc, buf, width, 0, height, TJPF_RGBX, &outbuf, &length, TJSAMP_444, quality, TJFLAG_FASTDCT);
  res.len = length;
  res.buf = outbuf;

  return res;

}

void free_encoded_image(void *buf) {

  tjFree(buf);

}

DecodeRes decode_image(TJContext *ctx, char *buf, unsigned long len) {

  int width;
  int height;
  int subsamp;
  unsigned char *outbuf;

  DecodeRes res;
  bzero(&res, sizeof(DecodeRes));

  tjDecompressHeader2(ctx->tj_dec, buf, len, &width, &height, &subsamp);
  outbuf = malloc(width * height * 4);
  tjDecompress2(ctx->tj_dec, buf, len, outbuf, width, 0, height,  TJPF_RGBX, TJFLAG_FASTDCT);
  res.width = width;
  res.height = height;
  res.buf = outbuf;

  return res;

}

void free_decoded_image(void *buf) {

  free(buf);

}
