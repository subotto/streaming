
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#include <time.h>

#include <cairo.h>
#include <turbojpeg.h>

#include "imgio.h"


TJContext *ctx;


inline static double timer() {

  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
  return ts.tv_sec + 1e-9 * ts.tv_nsec;

}

inline static void tic(double *clock, const char *desc) {

  double new_time = timer();
  fprintf(stderr, "> TIC! %f (%s)\n", new_time - *clock, desc);
  *clock = new_time;

}

void edit_frame(Image *image) {

  cairo_scale(image->ctx, image->width/4, image->height/3);
  cairo_set_source_rgb(image->ctx, 1.0, 0.0, 0.0);
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

  ctx = create_tjcontext();

  double clock = timer();
  double frame_clock = clock;
  while (1) {
    tic(&frame_clock, "frame_clock");
    tic(&clock, "new cycle");
    Image *image = read_frame(ctx, stdin);
    tic(&clock, "frame read");
    get_cairo_context(image);
    tic(&clock, "cairo context created");
    edit_frame(image);
    tic(&clock, "frame edited");
    cairo_surface_flush(image->surf);
    tic(&clock, "surface flushed");
    write_frame(ctx, stdout, image);
    tic(&clock, "frame written");
    free_image(image);
    tic(&clock, "cycle finished");
  }

  return 0;

}
