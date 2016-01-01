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

#include "list.h"
#include "pipe.h"

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
