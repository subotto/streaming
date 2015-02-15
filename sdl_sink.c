// Based on http://dranger.com/ffmpeg/tutorial02.c

// tutorial02.c
// A pedagogical video player that will stream through every video frame as fast as it can.
//
// Code based on FFplay, Copyright (c) 2003 Fabrice Bellard, 
// and a tutorial by Martin Bohme (boehme@inb.uni-luebeckREMOVETHIS.de)

#include <SDL.h>
#include <SDL_thread.h>

#include <stdio.h>

#include "imgio.h"

int main(int argc, char *argv[]) {
  int width, height;
  SDL_Overlay     *bmp;
  SDL_Surface     *screen;
  SDL_Rect        rect;
  SDL_Event       event;

  TJContext *ctx = create_tjcontext();

  if (argc != 3) {
    fprintf(stderr, "Usage: %s width height\n", argv[0]);
    exit(1);
  } else {
    width = atoi(argv[1]);
    height = atoi(argv[2]);
  }

  if(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER)) {
    fprintf(stderr, "Could not initialize SDL - %s\n", SDL_GetError());
    exit(1);
  }

  // Make a screen to put our video
  screen = SDL_SetVideoMode(width, height, 0, SDL_RESIZABLE);
  if(!screen) {
    fprintf(stderr, "SDL: could not set video mode - exiting\n");
    exit(1);
  }

  // Allocate a place to put our YUV image on that screen
  bmp = SDL_CreateYUVOverlay(width, height, SDL_YV12_OVERLAY, screen);

  // Read frames and save first five frames to disk
  while (1) {

    Image *image = read_frame_to_yuv(ctx, stdin);

    SDL_LockYUVOverlay(bmp);
    copy_yuv_to_planes(image, bmp->pitches, bmp->pixels, 1);
    SDL_UnlockYUVOverlay(bmp);
    free_image(image);

    rect.x = 0;
    rect.y = 0;
    rect.w = width;
    rect.h = height;
    SDL_DisplayYUVOverlay(bmp, &rect);

    SDL_PollEvent(&event);
    switch (event.type) {
    case SDL_QUIT:
      SDL_Quit();
      exit(0);
      break;
    default:
      break;
    }
  }

  return 0;
}
