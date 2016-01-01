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

#ifndef __MEMORY_H
#define __MEMORY_H

#define MAKE(type,ident) type*ident=(type*)xcalloc(sizeof(type))

#define MEMORY_CHECK
#ifdef MEMORY_CHECK
void*xmalloc(size_t s);
void*xcalloc(size_t s);
void*xrealloc(void*,size_t s);
void xmark();
int xmem(void*);
int xcheck();
void xfree(void*p);
#else
#define xmalloc(s)	malloc(s)
#define xcalloc(s)	calloc(1,s)
#define xrealloc(p,s)	realloc((p),(s))
#define xmark()		
#define xmem(p)		(1)
#define xcheck()	(0)
#define xfree(p)	free(p)
#endif
#endif
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

#ifndef __PIPE_H
#define __PIPE_H


/* pipe modes */
#define PIPE_RD 1
#define PIPE_WR 2

struct buffer;

/*
 * NB. all the "int i" etc. refer to a number/count of bytes
 */
#ifndef SWIG
struct pipe
{
  struct link k; /* owned by a task */
  struct buffer*b;
  struct pipe*next; /* next pipe on this buffer */
  unsigned int mode; /* PIPE_RD or PIPE_WR */
  int i; /* index into buffer mem */
  int i_lim; /* stop here (negative i_lim is infinity) */
  struct pipe*_next;  /* used for composite tasks. deprecated. */
  int id; /* unique among pipes */
};
#endif

typedef struct pipe*PIPE; 
typedef struct pipe*WRITER; 
typedef struct pipe*READER; 

struct pipe* pipe_alloc();
void pipe_init(struct pipe*p,int mode);
struct pipe* pipe_new(int mode);

void pipe_attach(struct pipe*p,struct buffer*);
void pipe_detach(struct pipe*p);

struct pipe* reader_new(struct buffer*b);
struct pipe* writer_new(struct buffer*b);

void pipe_reset(struct pipe*p);
char* pipe_str(struct pipe*p);
void pipe_print(struct pipe*p,int);
int pipe_id(struct pipe*p);

/*
 * must use the appropriate read/write call
 * depending on weather you have a read pipe or a write pipe
 */
unsigned int write_size(struct pipe*p); /* how much can we write? */
unsigned int read_size(struct pipe*p); /* how much can we read? */

void produce(struct pipe*p,int i); /* writers produce */
void consume(struct pipe*p,int i); /* readers consume */

int is_reader(struct pipe*p);
int is_writer(struct pipe*p);

void* reader_mem(struct pipe*p); /* do not call this unless read_size(p)>0 */
void* writer_mem(struct pipe*p); /* do not call this unless write_size(p)>0 */

/* ask for more read/write_size() */
int reader_request(struct pipe*p,int size);
int writer_request(struct pipe*p,int size);

/* move the pointer (must be stay within bounds) */
void reader_seek(struct pipe*p,int i);
void writer_seek(struct pipe*p,int i);

/* limit the data flow */
void pipe_limit(struct pipe*p, int i);
int pipe_get_limit(struct pipe*p);
void pipe_no_limit(struct pipe*p);

int pipe_get_i(struct pipe*p);

int pipe_done(struct pipe*p);

/* relative seek */
void _writer_nudge(struct pipe*p,int i);
void _reader_nudge(struct pipe*p,int i);

/* this _msg stuff has got to go */
int read_msg(struct pipe*p,char*c,int n);
#define MSG_LEN 128
int write_msg(struct pipe*p,char*c);

void pipe_free(struct pipe*);

#endif

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

#ifndef __OSC_H
#define __OSC_H

void
task_tri_set_f(struct task*t,float f);
void
task_tri_set_r(struct task*t,float r);
struct task*
task_tri_new(float f,float r);
void
task_squ_set_f(struct task*t,float f);
void
task_squ_set_r(struct task*t,float r);
struct task*
task_squ_new(float f,float r);

struct task_sin;

void
task_sin_set_p(struct task*_t,float p);
void
task_sin_set_f(struct task*t,float f);
void
task_sin_set_r(struct task*t,float r);
struct task*
task_sin_new(float freq,float r);

unsigned int
task_noise_send(struct task*t);
SIMPLE_TASK_DEF(noise);

#ifdef BUZZING_SOUNDS
struct task*
task_vdp_new(float e);

struct task*
task_chaos_new(float cx, float cy);
void
task_chaos_set_c(struct task*_t,float cx, float cy);
#endif

struct task*
task_poly_new(int nv, float r, int nu, float alpha );
void
task_poly_set_alpha(struct task*_t, float alpha);
void
task_poly_set_r(struct task*_t, float r);
void
task_poly_set_v(struct task*t, int i,float x);
float
task_poly_get_v(struct task*t, int i);

#endif
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

#ifndef __FILTER_H
#define __FILTER_H

struct task*
task_resample_new(float r);
void
task_resample_set_r(struct task*t, float r);

struct task*
task_fir_new(float*fir, int len );

struct tap;
void
tap_set_i(struct tap*tp,int i);
void
tap_set_x(struct tap*tp,int x);
struct task*
task_iir_new();
struct tap*
task_iir_add(struct task*_t,int i, int x);
void
task_iir_remove(struct task*_t,struct tap*tp);


struct task*
task_fdelta_new(float w);

struct task*
task_lo_new(float r);
void
task_lo_set_r(struct task*t,float r);

struct task*
task_hi_new(float r);
void
task_hi_set_r(struct task*t,float r);

struct task*
task_band_new( float r1, float r2 );
void
task_band_set_r(struct task*t,float r1,float r2);

struct task*
task_delta_new(float w);

struct task*
task_rlo1_new( float f, float r );
void
task_rlo1_set_r(struct task*t,float r);
void
task_rlo1_set_f(struct task*t,float f);

struct task*
task_rlo2_new( float f, float r );
void
task_rlo2_set_r(struct task*t,float r);
void
task_rlo2_set_f(struct task*t,float f);

struct task*
task_lookup_new(struct buffer*b);
void
task_lookup_flush(struct task*t);


#endif



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

#ifndef __BUF_H
#define __BUF_H


#ifndef SWIG
/*
 * This is your standard ring buffer.
 * The writer(s?) never overtake the readers and vice-versa.
 */
struct buffer
{
  struct link k;
  int id;

  char* mem; /* = malloc(size) */
  unsigned int size;

  int null; /* start reading here */
  int offset; /* start writing here */

  struct pipe *readers; /* head of linked list */
  struct pipe *writers; /* head of linked list */

};
#endif

/* typedef struct buffer*BUFFER;  */
/* typedef void (*UPDATE)(struct buffer*); */

struct buffer* buffer_new(unsigned int size); 
void buffer_reset(struct buffer*b);
int buffer_invariant(struct buffer*b);
void buffer_print(struct buffer*b );
int buffer_id(struct buffer*b);

void buffer_free(struct buffer*b);

/*
 * All the rest is usually called via the pipe_*() functions.
 */

void buffer_attach_reader(struct buffer*b,struct pipe*p);
void buffer_attach_writer(struct buffer*b,struct pipe*p);
void buffer_detach_reader(struct buffer*b,struct pipe*p);
void buffer_detach_writer(struct buffer*b,struct pipe*p);

/* update the buffer */
int buffer_send_read(struct buffer*b);
int buffer_send_write(struct buffer*b);
int buffer_send(struct buffer*b);

unsigned int buffer_read_size(struct buffer*b, int i);
unsigned int buffer_write_size(struct buffer*b, int i);
void* buffer_peek_read(struct buffer*b,int i);
void* buffer_peek_write(struct buffer*b,int i);

unsigned int buffer_request_read(struct buffer*b, int i, int size);
unsigned int buffer_request_write(struct buffer*b, int i, int size);

#endif
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

#ifndef __TERM_H
#define __TERM_H

struct task*
task_term_new();

void
task_term_set_line(struct task*_t,int i,char*line);

#endif
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

#ifndef __ARRAY_H
#define __ARRAY_H


struct array
{
  void*mem;
  int sz;
  void (*free)(struct array*);
  struct array*a; /* parent */
  int refc; 
  /*struct array *next, *prev;*/

  /* multidimensional ? */ 
  /* int *dim; */
  /* int *pitch;  */
};

typedef void (*A_FREE)(struct array*);

/* void array_init(struct array*a,A_FREE free); */

struct array*
array_new(int sz);
struct array*
array_new_mmap(char*filename);
struct array*
array_new_sub(struct array*a,int _i,int i);
void*
array_mem(struct array*a);
int
array_sz(struct array*a);
void
array_set_short(struct array*a, int i, short x);
short
array_get_short(struct array*a, int i);

void
array_free(struct array*a);

#endif
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

#ifndef __MY_SDL_H
#define __MY_SDL_H

/* #define HAVE_SDL */

#ifdef HAVE_SDL
#endif

/* extern Uint32 black, red,white,blue,green; */

struct task*
task_trace_new(int x0,int y0, int x1, int y1);

#define SIMPLE_TASK_DEF(name) struct task* task_##name##_new()

/* -> [int, int]* */
unsigned int
task_key_send(struct task*t);
SIMPLE_TASK_DEF(key);

#endif
