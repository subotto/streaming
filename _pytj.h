
#ifndef _PYTJ_H
#define _PYTJ_H

#include <turbojpeg.h>

typedef struct {
  tjhandle tj_enc;
  tjhandle tj_dec;
} TJContext;

typedef struct {
  void *buf;
  unsigned int width;
  unsigned int height;
} DecodeRes;

typedef struct {
  void *buf;
  unsigned long len;
} EncodeRes;

TJContext *create_tjcontext(void);
void free_tjcontext(TJContext *ctx);
EncodeRes encode_image(TJContext *ctx, unsigned long _buf, unsigned int width, unsigned int height, int pixel_format, int subsamp, int quality, int flags);
void free_encoded_image(void *buf);
DecodeRes decode_image(TJContext *ctx, char *buf, unsigned long len, int pixel_format, int flags);
void free_decoded_image(void *buf);

#endif
