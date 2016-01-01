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

#include "list.h"

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

