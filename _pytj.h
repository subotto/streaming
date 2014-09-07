
#ifndef _PYTJ_H
#define _PYTJ_H

typedef struct {
  tjhandle tj_enc;
  tjhandle tj_dec;
} TJContext;

TJContext *create_tjcontext(void);
void free_tjcontext(TJContext *ctx);
void *encode_image(TJContext *ctx, void *buf, unsigned int width, unsigned int height, unsigned int *res_len, int quality);
void free_encoded_image(void *buf);
void *decode_image(TJContext *ctx, void *buf, unsigned long len, unsigned int *res_width, unsigned int *res_height);
void free_decoded_image(void *buf);

#endif
