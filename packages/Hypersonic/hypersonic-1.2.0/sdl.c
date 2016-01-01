/*  Copyright (C) 2003 Simon Burton

    This file is part of hYPerSonic.
    
    hYPerSonic is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2.1 of the License, or
    (at your option) any later version.
    
    hYPerSonic is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with hYPerSonic; see the file COPYING. If not, write to the
    Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
    MA 02111-1307, USA.  */

#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <assert.h>

#include "sdl.h"
#include "memory.h"
#include "task.h"
#include "debug.h"

#ifdef HAVE_SDL
#include <SDL/SDL.h>
#if 0
#include <SDL/SDL_ttf.h>
#endif

/* singleton */
static SDL_Surface*screen=NULL;

static int width=640, height=480,depth=16;
static int bpp=0;
/*static int ptsize=40;*/
static int sdl_refcount=0;

Uint32 black, red,white,blue,green;
#define NCOLOURS 32
static Uint32 colour[NCOLOURS];
#define NBUFS NCOLOURS

static int gain=128;
static int speed=1;

void
sdl_init()
{
  Uint32 flags;
  int i;
  Uint32*pc;

  if (SDL_Init(SDL_INIT_VIDEO) < 0)
  {
    fprintf(stderr,"_Init failed: %s\n",
      SDL_GetError());
    exit(1);
  }
  atexit(SDL_Quit);
  flags= SDL_HWSURFACE|SDL_ANYFORMAT|SDL_DOUBLEBUF;
  flags= SDL_DOUBLEBUF;
  screen = SDL_SetVideoMode( width,height, depth, flags );
  if(screen==NULL)
  {
    fprintf(stderr,"SetVideoMode failed: %s\n",
      SDL_GetError());
    exit(1);
  }
  width=screen->w;
  height=screen->h;
  depth=screen->format->BitsPerPixel;
  bpp = screen->format->BytesPerPixel;

  black=SDL_MapRGB(screen->format,0,0,0);
  white=SDL_MapRGB(screen->format,255,255,255);
  red=SDL_MapRGB(screen->format,255,0,0);
  green=SDL_MapRGB(screen->format,0,255,0);
  blue=SDL_MapRGB(screen->format,0,0,255);
  for(pc=colour,i=0;i<256;i+=256/NCOLOURS,pc++)
    *pc=SDL_MapRGB(screen->format,0,256-i,i);
}

void
sdl_free()
{
  SDL_FreeSurface(screen);
  SDL_Quit();
}

#if 0
static TTF_Font *font=NULL;

void
font_init()
{
  char*filename;
  if( TTF_Init() < 0 )
  {
    fprintf(stderr,"TTF_Init failed: %s\n",
      SDL_GetError());
    exit(1);
  }
  atexit(TTF_Quit);

  filename= "/home/simon/home/c/sonic/fonts/ARCADE__.TTF";
  font=TTF_OpenFont(filename,ptsize);
  if ( font == NULL )
  {
    fprintf(stderr,
      "Couldn't load %d pt font from %s: %s\n",
      ptsize, filename, SDL_GetError());
    exit(2);
  }
  TTF_SetFontStyle(font,TTF_STYLE_NORMAL);
}

void
font_finalize()
{
  TTF_CloseFont(font);
  TTF_Quit();
}
#endif

#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define BND(a,b,c) MIN(MAX(a,b),c)
#define SGN(x) ((x)>0?1:((x)==0?0:(-1)))
#define ABS(x) ((x)>0?(x):(-x))

void
mod_gain(int mod)
{
  if(mod>0) gain*=2;
  else if(mod<0) gain=MAX(gain/2,1);
}

void
mod_speed(int mod)
{
  if (mod>0) speed*=2;
  else if (mod<0) speed=MAX(speed/2,1);
}

void
sdl_incref()
{
  sdl_refcount++;
  if(screen==NULL)
    sdl_init();
}

void
sdl_decref()
{
  sdl_refcount--;
  if(!sdl_refcount)
    sdl_free();
}

/* -> [int on, int key]* */
unsigned int
task_key_send(struct task*t)
{
  SDL_Event event;
  int i=0;
  int n;
  struct pipe*p;

  p=writer(t);
  if(!p)return 0;

  n=write_size(p);

  if(screen==NULL)
    sdl_incref(); /* hack */
  assert(screen);

  for(; SDL_PollEvent(&event)>0 && 10 /*hack*/ < n ; n=write_size(p))
  {
    /* we got an event */
    int sym=0;
    int ret;
    char*wmem;
    wmem=(char*)writer_mem(p);
    switch(event.type)
    {
      case SDL_QUIT:
        exit(0); 
      break;
      case SDL_KEYDOWN: 
        sym= event.key.keysym.sym;
        ret=snprintf(wmem,n,"1 %d", sym); 
        assert(ret>0);
        produce(p,ret+1);
        i+=ret+1;
        /*printf("task_key_send: keydown %d\n", wmem[1] );*/
      break;
      case SDL_KEYUP:
        sym= event.key.keysym.sym;
        ret=snprintf(wmem,n,"0 %d", sym); 
        assert(ret>0);
        produce(p,ret+1);
        i+=ret+1;
        /*printf("task_key_send: keyup %d\n", wmem[1] );*/
      break;
    }
  }
  /* if(i)  printf("%d events\n",i); */
  return i; 
}
SIMPLE_TASK(key)


void
sdl_pixel(int x,int y,int c)
{
  /*printf("%d,%d\n",x,y);*/
  memcpy(screen->pixels+screen->pitch*y+x*bpp, &c, bpp);
}

struct task_trace
{
  struct task t;
  int x0,y0,x1,y1;
  int x;
  int *y;
  int colour;
};

unsigned int
task_trace_send(struct task_trace*t);
void
task_trace_free(struct task_trace*t);

struct task*
task_trace_new(int x0,int y0, int x1, int y1)
{
  struct task_trace*t;
  int i;
  sdl_incref();
  t=(struct task_trace*)xcalloc(sizeof(struct task_trace));
  task_init( (TASK)t,NULL,(SEND)task_trace_send,(FREE)task_trace_free);
  t->x0=x0; t->x1=x1; t->y0=y0; t->y1=y1;
  /* printf("task_trace_new(%d,%d,%d,%d);\n",x0,y0,x1,y1); */
  t->x=x0;
  assert(x1>x0);
  t->y=(int*)xmalloc(sizeof(int)*(x1-x0));
  for(i=0;i<(x1-x0);i++)
    t->y[i]=(y1-y0)/2;
  t->colour=green;
  return (TASK)t;
}

/* short -> */
unsigned int
task_trace_send(struct task_trace*t)
{
#define FRAMES 10
  static int fcount=FRAMES;
  unsigned int count=0;
  unsigned int size=0;
  struct pipe*rp;
  short*rmem;
  assert(xmem(t));
  /*printf("fcount=%d\n",fcount);*/
#ifdef SKIP_SOME
  if(fcount)
  {
    fcount--;
    return task_null_send((TASK)t);
  }
#endif
  rp=reader((TASK)t);
  if(!rp)return 0;
  size=read_size(rp);
  if(!size)return 0;
  rmem=reader_mem(rp);
  //printf("trace: mem=%p size=%d\n",  rmem, size );
#if 0
  wp=writer((TASK)t);
  if(wp)
  {
    size=MIN(size,write_size(wp));
    if(!size) return 0;
    wmem=writer_mem(wp);
  }
#endif
  //task_null_send((TASK)t);
  if(size)
  {
    int j=0;
    fcount=FRAMES; 
    /*printf("<size %d>",size);*/
#if 1
    if(size/2 > t->x1-t->x0)
      /* skip start */
      j= size/2 + t->x0-t->x1;
#endif
    SDL_LockSurface(screen);
    for(;j<size/2;j++)
    {
      /* short y=(t->y1-t->y0)/2+rmem[j]*gain/(1<<15); */
      short y=t->y0+(t->y1-t->y0)/2+((rmem[j]*gain)>>15);
      sdl_pixel(t->x+t->x0,t->y[t->x],0);
      t->y[t->x]=y;
      sdl_pixel(t->x+t->x0,y,t->colour);
      t->x=(t->x+1)%(t->x1-t->x0);
    }
    SDL_UnlockSurface(screen);
    SDL_Flip(screen);
  }
  if(size)
  {
    count+=size;
    consume(rp,size);
#if 0
    if(wp)
    {
      memcpy(wmem,rmem,size);
      produce(wp,size);
      count+=size;
    }
#endif
  }
  return count;
}

void
task_trace_free(struct task_trace*t)
{
  assert(t);
  xfree(t->y);
}

#if 0

void
__trace_send(
  struct task_trace*t,
  short*buf,
  int ilen, /* length of buf */
  int olen /* pixels */ )
{
  int x;
  int i,di;
  assert(t->x1>t->x0);
  di=ilen/olen;
  assert(t);
  SDL_LockSurface(screen);
  for(
    x=0,i=0;
    x<olen;
    x++,i+=di,t->x++)
  {
    int ymin,ymax,_i;
    if(t->x==t->x1)
      t->x=t->x0;
    /*assert(i+di<=ilen);*/
    ymin=ymax=buf[i];
    for(_i=i+1;_i<i+di&&_i<ilen;_i++)
    {
       if(buf[_i]>ymax)ymax=buf[_i];
       if(buf[_i]<ymin)ymin=buf[_i];
    }
    ymin*=gain;
    ymax*=gain;
    ymin/=32000;
    ymax/=32000;
    ymin+=(t->y1-t->y0)/2;
    ymax+=(t->y1-t->y0)/2;
    assert(ymin<=ymax);
    if(ymax<t->y0) continue;
    if(ymin>=t->y1) continue;
    ymin=MAX(t->y0,ymin);
    ymax=MIN(t->y1-1,ymax);
    assert(t->x>=t->x0&&t->x<t->x1);

    {
      int*_y=t->y+(t->x-t->x0)*2,__y;
      for(__y=_y[0];__y<_y[1]+1;__y++)
        sdl_pixel(t->x,__y,black);
      _y[0]=ymin;_y[1]=ymax;
      for(__y=_y[0];__y<_y[1]+1;__y++)
        sdl_pixel(t->x,__y,t->colour);
    }

  }
  SDL_UnlockSurface(screen);
}

#endif

#else

struct task*
task_trace_new(int x0,int y0, int x1, int y1)
{
  return NULL;
}


unsigned int
task_key_send(struct task*t)
{
  return 0;
}
SIMPLE_TASK(key)

#endif /* HAVE_SDL */

