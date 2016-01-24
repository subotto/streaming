
#include <stdlib.h>
#include <strings.h>

#include "pytj.h"

// FIXME: error handling
TJContext *create_tjcontext(void) {

  TJContext *ctx = (TJContext*) malloc(sizeof(TJContext));
  if (ctx == NULL) return NULL;

  ctx->tj_enc = tjInitCompress();
  ctx->tj_dec = tjInitDecompress();

  return ctx;

}

void free_tjcontext(TJContext *ctx) {

  if (ctx == NULL) return;

  tjDestroy(ctx->tj_enc);
  tjDestroy(ctx->tj_dec);
  free(ctx);

}

// The buffer is assumed to be width * height * 4; buffer address is
// passed as unsigned long (instead of unsigned char*) in order to
// simplify interface with Python
// FIXME: error handling
EncodeRes encode_image(TJContext *ctx, unsigned long _buf, unsigned int width, unsigned int height, int pixel_format, int subsamp, int quality, int flags) {

  unsigned long length;
  unsigned char *buf = (unsigned char*) _buf;
  unsigned char *outbuf = NULL;

  EncodeRes res;
  bzero(&res, sizeof(EncodeRes));

  tjCompress2(ctx->tj_enc, buf, width, 0, height, pixel_format, &outbuf, &length, subsamp, quality, flags);
  res.len = length;
  res.buf = outbuf;

  return res;

}

void free_encoded_image(void *buf) {

  tjFree((unsigned char*) buf);

}

// FIXME: error handling
DecodeRes decode_image(TJContext *ctx, char *buf, unsigned long len, int pixel_format, int flags) {

  int width;
  int height;
  int subsamp;
  unsigned char *outbuf;

  DecodeRes res;
  bzero(&res, sizeof(DecodeRes));

  tjDecompressHeader2(ctx->tj_dec, (unsigned char*) buf, len, &width, &height, &subsamp);
  outbuf = (unsigned char*) malloc(width * height * 4);
  tjDecompress2(ctx->tj_dec, (unsigned char*) buf, len, outbuf, width, 0, height, pixel_format, flags);
  res.width = width;
  res.height = height;
  res.buf = outbuf;
  res.subsamp = subsamp;

  return res;

}

void free_decoded_image(void *buf) {

  free(buf);

}

// FIXME: error handling
DecodeYUVRes decode_image_to_yuv(TJContext *ctx, char *buf, unsigned long len, int flags) {

  int width;
  int height;
  int subsamp;
  unsigned char *outbuf;

  DecodeYUVRes res;
  bzero(&res, sizeof(DecodeYUVRes));

  tjDecompressHeader2(ctx->tj_dec, (unsigned char*) buf, len, &width, &height, &subsamp);
  unsigned long outbuf_len = tjBufSizeYUV(width, height, subsamp);
  outbuf = (unsigned char*) malloc(outbuf_len);
  tjDecompressToYUV(ctx->tj_dec, (unsigned char*) buf, len, outbuf, flags);
  res.width = width;
  res.height = height;
  res.buf = outbuf;
  res.len = outbuf_len;
  res.subsamp = subsamp;

  return res;

}

void free_decoded_yuv_image(void *buf) {

  free(buf);

}
