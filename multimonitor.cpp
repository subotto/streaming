
#include <SDL.h>
#include <SDL_thread.h>

#include "net.hpp"

using namespace chrono;

int main() {

  int width = 800;
  int height = 600;
  double fps = 15.0;
  SDL_Overlay *bmp;
  SDL_Surface *screen;
  SDL_Rect rect;

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
  bmp = SDL_CreateYUVOverlay(width, height, SDL_YV12_OVERLAY, screen);

  vector< ImageServerConf > servers;
  servers.emplace_back("localhost", "2204", 10.0);
  servers.emplace_back("localhost", "2205", 10.0);
  ImageMultiClient client(servers);

  bool running = true;
  while (running) {
    // Get a new set of frames
    while (true) {
      auto res = client.advance_to_stream(0, false);
      if (res.size() == 0) break;
    }
    client.print_status();

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
