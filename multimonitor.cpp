
#include <SDL.h>
#include <SDL_thread.h>

#include <assert.h>

#include "net.hpp"

using namespace chrono;

static inline SDL_Rect build_rect(int x, int y, int w, int h) {

  SDL_Rect r;
  r.x = x;
  r.y = y;
  r.w = w;
  r.h = h;
  return r;

}

static inline SDL_Rect get_rect(int width, int height, int num, int tot) {

  switch (tot) {
  case 1:
    return build_rect(0, 0, width, height);
  case 2:
    switch (num) {
    case 0:
      return build_rect(0, 0, width, height / 2);
    case 1:
      return build_rect(0, height / 2, width, height / 2);
    }
  case 3:
    switch (num) {
    case 0:
      return build_rect(0, 0, width, height / 2);
    case 1:
      return build_rect(0, height / 2, width / 2, height / 2);
    case 2:
      return build_rect(width / 2, height / 2, width / 2, height / 2);
    }
  case 4:
    switch (num) {
    case 0:
      return build_rect(0, 0, width / 2, height / 2);
    case 1:
      return build_rect(width / 2, 0, width / 2, height / 2);
    case 2:
      return build_rect(0, height / 2, width / 2, height / 2);
    case 3:
      return build_rect(width / 2, height / 2, width / 2, height / 2);
    }
  }

  assert(false);

}

int main() {

  int width = 800;
  int height = 600;
  double fps = 15.0;
  SDL_Surface *screen;

  // Initialize SDL
  if(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER)) {
    fprintf(stderr, "Could not initialize SDL - %s\n", SDL_GetError());
    exit(1);
  }
  screen = SDL_SetVideoMode(width, height, 0, SDL_RESIZABLE);
  if(!screen) {
    fprintf(stderr, "SDL: could not set video mode - exiting\n");
    exit(1);
  }

  vector< ImageServerConf > servers;
  servers.emplace_back("localhost", "2204", 10.0);
  servers.emplace_back("localhost", "2205", 10.0);
  ImageMultiClient client(servers, IM_OP_YUV_DECODE);

  vector< SDL_Overlay* > overlays;
  overlays.resize(servers.size());

  bool running = true;
  while (running) {
    // Get a new set of frames (FIXME: implement frame skipping)
    vector< const Image * > res = client.advance_to_last(false);
    client.print_status();

    // Show the frames
    if (res.size() > 0) {
      for (unsigned int i = 0; i < servers.size(); i++) {
        auto &image = res[i];
        if (image != NULL) {
          auto &overlay = overlays[i];
          if (overlay == NULL) {
            overlay = SDL_CreateYUVOverlay(image->width, image->height, SDL_YV12_OVERLAY, screen);
          }
          SDL_LockYUVOverlay(overlay);
          copy_yuv_to_planes(image, overlay->pitches, overlay->pixels, 1);
          SDL_UnlockYUVOverlay(overlay);

          SDL_Rect rect = get_rect(width, height, i, servers.size());
          SDL_DisplayYUVOverlay(overlay, &rect);
        }
      }
    }

    // Query for SDL events
    while (true) {
      SDL_Event event;
      int res;
      res = SDL_PollEvent(&event);
      if (!res) break;

      switch (event.type) {
      case SDL_QUIT:
        running = false;
        break;

      case SDL_VIDEORESIZE:
        // Braces to limit the scope of resevent and avoid triggering
        // warnings related to switch jumps
        {
          SDL_ResizeEvent &resevent = event.resize;
          width = resevent.w;
          height = resevent.h;
          screen = SDL_SetVideoMode(width, height, 0, SDL_RESIZABLE);
        }
        break;

      default:
        break;
      }
    }

    // Wait a bit before next frame
    this_thread::sleep_for(microseconds(int(1e6 / fps)));
  }

  SDL_Quit();

  return 0;

}
