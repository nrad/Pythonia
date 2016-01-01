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

#ifndef __TASK_H
#define __TASK_H
#include "pipe.h"
#include "buffer.h"
#include <Python.h>
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))

struct buffer;
struct task;

#ifndef SWIG
struct task
{
  /* inherit from struct link so we can be in someone else's list */
  struct link k;

  struct list readers; /* reader pipes */
  struct list writers; /* writer pipes */

/*
 * virtual functions for customising behaviour
 */
  void (*reset)(struct task*); /* go back to initial state */
  /*
   * do all processing in the send.
   * Should return number indicating how much processing was done, 0 if nothing changed.
   */
  unsigned int (*send)(struct task*);

  /* t->free should not free t, only any extra malloced memory etc. */
  void (*free)(struct task*);

  void (*assert)(struct task*); /* any integrity checks */

  /* put here for tricky things like compound tasks. deprecated for now. */
  struct pipe* (*open_reader)(struct task*,struct buffer*);
  void (*close_reader)(struct task*,struct pipe*);
  struct pipe* (*open_writer)(struct task*,struct buffer*);
  void (*close_writer)(struct task*,struct pipe*);

  /* not used */
  void (*str)(struct task*,char*c,int n); /* snprintf */

  int done; /* set this when task won't do anymore without a reset */
  int id; /* unique id among tasks */
  int i; /* accumulated from send calls */
};
#endif

typedef struct pipe* (*OPEN_READER)(struct task*,struct buffer*);
typedef void (*CLOSE_READER)(struct task*,struct pipe*);
typedef struct pipe* (*OPEN_WRITER)(struct task*,struct buffer*);
typedef void (*CLOSE_WRITER)(struct task*,struct pipe*);

typedef struct pipe*(*READER_NEW)(struct buffer*,int);
typedef struct pipe*(*WRITER_NEW)(struct buffer*,int);
typedef struct task*TASK; /* don't use me */
typedef void (*RESET)(struct task*);
typedef unsigned int (*SEND)(struct task*);
typedef void (*FREE)(struct task*);
typedef void (*ASSERT)(struct task*);

/*
void task_init(struct task*t,
  void (*reset)(struct task*), 
  unsigned int (*send)(struct task*),
  void (*free)(struct task*));
*/
void task_init(struct task*t,RESET reset, SEND send, FREE free);

void task_set_assert(struct task*t,ASSERT a);

struct task* task_new(SEND send);

void task_reset(struct task*t);

int task_id(struct task*t);

char* task_str(struct task*t);

void task_print(struct task*t);

/* fatal error */
void task_error(struct task*t,char*msg);
/* non fatal */
void task_msg(struct task*t,char*msg);

struct pipe* open_reader(struct task*t,struct buffer*b);
void close_reader(struct task*t,struct pipe*p);

struct pipe* open_writer(struct task*t,struct buffer*b);
void close_writer(struct task*t,struct pipe*p);

struct pipe* writer(struct task*t);
struct pipe* reader(struct task*t);
struct pipe* next_writer(struct task*t,struct pipe*p);
struct pipe* next_reader(struct task*t,struct pipe*p);

void task_set_done(struct task*t,int done);
int task_is_done(struct task*t);

unsigned int task_send(struct task*t);
void task_free(struct task*t);

/* from W.R. Stevens APUE */
void set_fl(int fd, int flags); /* flags are file status flags to turn on */

/******** simple tasks **********/

#define SIMPLE_TASK(name) \
struct task* task_##name##_new() {return task_new(task_##name##_send);}

/* put in each .h file manually, for SWIG */
#define SIMPLE_TASK_DEF(name) struct task* task_##name##_new()

unsigned int task_null_send(struct task*t);
SIMPLE_TASK_DEF(null);

unsigned int task_zero_send(struct task*t);
SIMPLE_TASK_DEF(zero);

unsigned int task_dummy_send(struct task*t);
SIMPLE_TASK_DEF(dummy);

unsigned int task_keen_send(struct task*t);
SIMPLE_TASK_DEF(keen);

unsigned int task_copy_send(struct task*t);
SIMPLE_TASK_DEF(copy);

unsigned int task_invert_send(struct task*t);
SIMPLE_TASK_DEF(invert);

unsigned int task_mean_send(struct task*t);
SIMPLE_TASK_DEF(mean);

unsigned int task_mix2_send(struct task*t);
SIMPLE_TASK_DEF(mix2);

unsigned int task_mix4_send(struct task*t);
SIMPLE_TASK_DEF(mix4);

unsigned int task_mix8_send(struct task*t);
SIMPLE_TASK_DEF(mix8);

unsigned int task_add_send(struct task*t);
SIMPLE_TASK_DEF(add);

unsigned int task_rmod_send(struct task*t);
SIMPLE_TASK_DEF(rmod);

unsigned int task_rmod8_send(struct task*t);
SIMPLE_TASK_DEF(rmod8);

unsigned int task_abs_send(struct task*t);
SIMPLE_TASK_DEF(abs);

unsigned int task_readln_send(struct task*t);
SIMPLE_TASK_DEF(readln);

unsigned int task_8b16_send(struct task*t);
SIMPLE_TASK_DEF(8b16);

unsigned int task_split_send(struct task*t);
SIMPLE_TASK_DEF(split);

unsigned int task_merge_send(struct task*t);
SIMPLE_TASK_DEF(merge);

unsigned int task_interleave_send(struct task*t);
SIMPLE_TASK_DEF(interleave);

unsigned int task_cat_send(struct task*t);
SIMPLE_TASK_DEF(cat);

unsigned int task_print_short_send(struct task*t);
SIMPLE_TASK_DEF(print_short);

struct task* task_none_new();

unsigned int task_env_send(struct task*t);
SIMPLE_TASK_DEF(env);

unsigned int task_rms_send(struct task*t);
SIMPLE_TASK_DEF(rms);

unsigned int task_amp_send(struct task*t);
SIMPLE_TASK_DEF(amp);

/****** complex tasks (maintain state info) *********/

struct task* task_mix_new(float r);
void task_mix_set_r(struct task*t,float r);

struct task* task_gain_new(float r);
void task_gain_set_r(struct task*t,float r);

struct task* task_delay_new(int n);
void task_delay_set_n(struct task*t,int n);

struct task* task_skip_new(float sk);

struct task* task_loop_new(void*mem, int size );
struct task* task_mem_rd_new(void*mem, int size );
struct task* task_mem_wr_new(void*mem, int size );
void task_mem_seek(struct task*_t, int offset);
int task_mem_get_offset(struct task*_t);

struct task* task_fd_rd_new(int fd);
struct task* task_fd_wr_new(int fd);
int task_fd_seek(struct task*t, int offset);

struct task* task_file_wr_new(char*filename);
struct task* task_file_rd_new(char*filename);

void set_nonblock(int fd);

#ifdef HAVE_JOYSTICK
struct task* task_joy_new();
struct task* task_axis_new(int n,float min,float max); 
struct task* task_button_new(int n); 
#endif

void set_vol(int num, int dev, int vol);
void set_recsrc(int dev, int chn);

struct task* task_dsp_rd_new(int dev, int srate, int stereo);
struct task* task_dsp_wr_new(int dev, int srate, int stereo);
struct task* task_dsp_rdwr_new(int dev, int srate, int stereo);

struct task* task_portaudio_new( int ichans, int ochans, int fpb, int dev, int srate );  
/* struct task* task_portaudio_new( PyObject*cb, PyObject*args, int ichans, int ochans, int fpb, int dev, int srate );  */
void task_portaudio_start( struct task*_t, PyObject*cb, PyObject*args ); 
/* void task_portaudio_start( struct task*_t ); */
void task_portaudio_stop( struct task*_t );

struct task*	task_usleep_new(int usec);
struct task* task_snatch_new(float f,char*fmt);
struct task* task_find_new();

void task_snatch_set_f(struct task*_t,float f);

struct task* task_msg_wrap_new(char* fmt);

struct task* task_midi_rd_new(char* on_fmt, char* off_fmt, char* clock);

float ntof(unsigned char a);
float vtor(unsigned char a);
int ftos(float f);
int ntos(unsigned char a);

struct task* task_linear_new(int n, short x_init);
void task_linear_setitem(struct task*_t, unsigned int idx, int di, int x);
void task_linear_append(struct task*_t, int di, int x);
void task_linear_pop(struct task*t);

#if 0
void task_linear_set_dx(struct task*t,int dx);
#endif

#endif


