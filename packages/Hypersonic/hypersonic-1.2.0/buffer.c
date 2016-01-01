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

#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include "buffer.h"
#include "pipe.h"
#include "memory.h"
#include "list.h"
#include "debug.h"

#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL 0
#endif

static char*tmem=NULL; /* for temporary use */
static int tsz=0;
static int tref=0;

struct buffer*
buffer_alloc()
{
  struct buffer*b;
  b=(struct buffer*)xcalloc(sizeof(struct buffer));
  assert(xmem(b));
  return b;
}

void
buffer_init(
  struct buffer*b,
  unsigned int size,
  void (*send)(struct buffer*))
{
  static int id=0;
  assert(xmem(b));
  ENTER();
  b->id=id++;
  b->size=size; /* default */
  b->mem=xmalloc(b->size);
  b->readers=NULL;
  b->writers=NULL;

  DBM(1, printf("buffer_new(%d)=b%d\n",size,b->id));
  b->null=0;
  b->offset=0;
  /* buffer_reset(b); */

  /* may need room to move */
  if(tref==0||tmem==NULL||tsz==0)
  { assert(tmem==NULL); assert(tsz==0); assert(tref==0); }
  if(tsz<size)
  {
    /* at least as big as i am */
    tsz=size;
    tmem=xrealloc(tmem,tsz);
  }
  tref++;

  LEAVE();
}

struct buffer*
buffer_new(unsigned int size)
{
  struct buffer*b;
  b=buffer_alloc();
  buffer_init(b,size,NULL);
  return b;
}

void 
buffer_reset(struct buffer*b)
{
  assert(xmem(b));
  ENTER();
  DBM(1, printf("buffer_reset(b%d)\n",b->id));
  b->null=0;
  b->offset=0;
  LEAVE();
}

int
buffer_invariant(struct buffer*b)
{
  assert(xmem(b));
  if( b->offset < b->null )
  {
    DBM(1,printf("buffer_invariant(b%d) b->offset < b->null \n", b->id ));
    return 0;
  }
  if( b->offset-b->null > b->size)
  {
    DBM(1,printf("buffer_invariant(b%d) b->offset-b->null > b->size)\n", b->id ));
    return 0;
  }
  return 1;
}

/* int */
/* buffer_sz(struct buffer*b) */
/* { */
/* } */

int
buffer_id(struct buffer*b)
{
  assert(xmem(b));
  return b->id;
}

void
buffer_print(struct buffer*b)
{
  assert(xmem(b));
  printf("<b%d=%p[null=%d,offset=%d,size=%d]>\n",
    b->id,b,b->null,b->offset,b->size);
}

/**********************************************************/

void
buffer_attach_reader(struct buffer*b,struct pipe*p)
{
  ENTER();
  assert(xmem(b));
  assert(xmem(p));
  assert(is_reader(p));
  DBM(1, printf("buffer_attach_reader(b%d,p%d)\n",b->id,p->id));
  p->next=b->readers;
  b->readers=p;
  LEAVE();
}

void
buffer_attach_writer(struct buffer*b,struct pipe*p)
{
  ENTER();
  assert(xmem(b));
  assert(xmem(p));
  assert(is_writer(p));
  DBM(1, printf("buffer_attach_writer(b%d,p%d)\n",b->id,p->id));
  /* assert(b->writers==NULL); */
  if(b->writers)
    printf(
      "WARNING buffer_attach_writer(b%d,p%d): multiple writers\n",
      b->id,p->id);
  p->next=b->writers;
  b->writers=p;
  LEAVE();
}

/**********************************************************/

#define MAX(a,b) ((a>b)?a:b)
#define MIN(a,b) ((a<b)?a:b)

int
buffer_send_read(struct buffer*b)
{
  struct pipe*p=NULL;
  int min;
  int count;
  ENTER();
  assert(xmem(b));
  /*if(b->readers==NULL) return 0;*/
  if(b->readers==NULL)
    printf("WARNING: buffer_send_read: b%d has no readers.\n",
      b->id );
  min=b->offset;
  for(p=b->readers;p;p=p->next)
  {
    int i;
    i = p->i; /* may change concurrently */
    assert(i<=b->offset);
    assert(i>=b->null);
    /* printf("buffer p%d ->i=%d\n", p->id, i ); */
    if(i<min) min=i;
  }
  DBM(2, printf("buffer_send_read(b%d): %d\n", b->id, min-b->null ));
  count=min-b->null;
  b->null=min;
  /* buffer_print(b); */
  assert(buffer_invariant(b));
  LEAVE();
  return count;
}

int
buffer_send_write(struct buffer*b)
{
  struct pipe*p=NULL;
  int min;
  int count=0;
  ENTER();
  assert(xmem(b));
  /*if(b->writers==NULL) return 0;*/
  if(b->writers==NULL)
    printf("WARNING: buffer_send_write: b%d has no writers.\n",
      b->id );
  min=b->offset+b->size;
  for(p=b->writers;p;p=p->next)
  {
    int i;
    i = p->i; /* may change concurrently */
    assert(i<=b->offset+b->size);
    if(i<min) min=i;
  }
  DBM(2, printf("buffer_send_write(b%d):  %d\n", 
    b->id, min-b->offset ));
  {
    count=min-b->offset;
    b->offset=min;
  }
  /* printf("offset %d\n", b->offset ); */

  assert(buffer_invariant(b));
  LEAVE();
  return count;
}

int
buffer_send(struct buffer*b)
{
  int count=0;
  count+=buffer_send_write(b);
  count+=buffer_send_read(b);
  return count;
}

/**********************************************************/

void
buffer_detach_reader(struct buffer*b,struct pipe*p)
{
  struct pipe*_p;
  ENTER();
  assert(xmem(b));
  assert(xmem(p));
  assert(is_reader(p));
  DBM(1, printf("buffer_detach_reader(b%d,p%d)\n",b->id,p->id));
  if(b->readers==p)
  {
    b->readers=p->next; /* skip */
    LEAVE();
    return;
  }
  else
  for(_p=b->readers;_p;_p=_p->next)
    if(_p->next==p)
    {
      _p->next=p->next; /* skip */
      LEAVE();
      return;
    }
  assert(0);
  LEAVE();
}

void
buffer_detach_writer(struct buffer*b,struct pipe*p)
{
  struct pipe*_p;
  ENTER();
  assert(xmem(b));
  assert(xmem(p));
  assert(is_writer(p));
  DBM(1, printf("buffer_detach_writer(b%d,p%d)\n",b->id,p->id));
  if(b->writers==p)
  {
    b->writers=p->next /* skip */;
    LEAVE();
    return;
  }
  for(_p=b->writers;_p;_p=_p->next)
    if(_p->next==p)
    {
      _p->next=p->next; /* skip */
      LEAVE();
      return;
    }
  assert(0);
  LEAVE();
}

/**********************************************************/

/* how big a block can we read at i ? */
unsigned int
buffer_read_size(struct buffer*b, int i)
{
  assert(xmem(b));
  assert(buffer_invariant(b));
  assert(i>=b->null&&i<=b->offset);
  return MIN(b->size-i%b->size,b->offset-i);
}

/* how big a block can we write at i ? */
unsigned int
buffer_write_size(struct buffer*b, int i)
{
  assert(xmem(b));
  assert(buffer_invariant(b));
  assert(i>=b->offset&&i<=b->null+b->size);
  return MIN(b->size-i%b->size,b->size+b->null-i);
}

/**********************************************************/

/* #define DEBUG_LEVEL 0 */

static void
_nudge_pipes(struct buffer*b,int i)
{
  struct pipe*p;
  assert(xmem(b));
  for(p=b->readers;p;p=p->next)
    _reader_nudge(p,i);
  for(p=b->writers;p;p=p->next)
    _writer_nudge(p,i);
}

static void
_rotate(struct buffer*b,int i)
{
  int _i;
  ENTER();
  assert(xmem(b));
  DBM(1,printf("_rotate(b%d,%d)\n", b->id, i ));
  if(i==0) return;
  _i=i%b->size;
  /* swap mem[_i] to mem[0] */
  memcpy(tmem,b->mem,b->size);
  memcpy(b->mem,tmem+_i,b->size-_i);
  memcpy(b->mem+b->size-_i,tmem,_i);
#ifdef FASTER
  if(2_i>b->size)
  {
    memcpy(tmem,b->mem+_i,b->size-_i);
    memmove(b->mem+b->size-_i,b->mem,_i);
    memcpy(b->mem,tmem,b->size-_i);
  }
  else
  {
    memcpy(tmem,b->mem,_i);
    memmove(b->mem+_i,b->mem,b->size-_i);
    memcpy(b->mem+b->size-_i,tmem,_i);
  }
#endif
  _i=b->size-_i;
  b->null+=_i;
  b->offset+=_i;
  _nudge_pipes(b,_i);
  LEAVE();
}

/* advance null to block boundary */
static void
_position_null(struct buffer*b)
{
  ENTER();
  assert(xmem(b));
  DBM(1,printf("_position_null b%d\n", b->id ));
  DBM(1,buffer_print(b));
  _rotate(b,b->null);
  assert(b->null%b->size==0);
  assert(buffer_invariant(b));
  LEAVE();
}

/* advance offset to block boundary */
static void
_position_offset(struct buffer*b)
{
  ENTER();
  assert(xmem(b));
  DBM(1,printf("_position_offset b%d\n", b->id ));
  DBM(1,buffer_print(b));
  _rotate(b,b->offset);
  assert(b->offset%b->size==0);
  assert(buffer_invariant(b));
  LEAVE();
}

/* try to find size bytes for read */
unsigned int
buffer_request_read(struct buffer*b, int i, int size)
{
  int sz;
  assert(xmem(b));
  assert(buffer_invariant(b));
  assert(i>=b->null&&i<=b->offset);
  DBM(1,printf("buffer_request_read(b%d,%d,%d)\n", b->id,i,size ));
  DBM(1,buffer_print(b));
  buffer_send_read(b);
  sz=MIN(b->size - i%b->size, b->offset - i);
  if(sz>=size)
    return sz;
  if(size>b->size)
  {
    DBM(0,printf("buffer_request_read(b%d,%d,%d)\n", b->id,i,size ));
    fprintf(stderr,"buffer too small\n");
    assert(0); /* grow_buffer */
  }
  if(b->offset - b->null < size)
    return sz; /* not ready */
  _position_null(b);
  return b->offset-b->null;
}

/* try to find size bytes for write */
unsigned int
buffer_request_write(struct buffer*b, int i, int size)
{
  int sz;
  assert(xmem(b));
  assert(buffer_invariant(b));
  assert(i>=b->offset&&i<=b->null+b->size);
  DBM(1,printf("buffer_request_write(b%d,%d,%d)\n", b->id,i,size ));
  DBM(1,buffer_print(b));
  buffer_send_write(b);
  sz=MIN(b->size-i%b->size,b->size+b->null-i);
  if(sz>=size)
    return sz;
  if(size>b->size)
  {
    fprintf(stderr,"buffer too small\n");
    assert(0); /* grow_buffer */
  }
  if(b->null+b->size-b->offset<size)
    return sz; /* not ready */
  _position_offset(b);
  return b->null+b->size-b->offset;
}

/**********************************************************/

void*
buffer_peek_read(struct buffer*b,int i)
{
  assert(xmem(b));
  assert(buffer_invariant(b));
  assert(i>=b->null);
  /* printf("buffer_peek_read i=%d, b->offset=%d\n", i, b->offset ); */
  assert(i<b->offset);
  return ((char*)b->mem)+i%b->size;
}

void*
buffer_peek_write(struct buffer*b,int i)
{
  assert(xmem(b));
  assert(buffer_invariant(b));
  assert(i>=b->offset);
  assert(i<b->null+b->size);
  return ((char*)b->mem)+i%b->size;
}

/**********************************************************/

void 
buffer_free(struct buffer*b)
{
  ENTER();
  assert(xmem(b));
  if(b->readers!=NULL)
  {
    printf("ERROR: buffer_free, b->readers!=NULL *** ");
    buffer_print(b);
    assert(0);
  }
  if(b->writers!=NULL)
  {
    printf("ERROR: buffer_free, b->writers!=NULL *** ");
    buffer_print(b);
    assert(0);
  }
  DBM(1, printf("buffer_free(b%d)\n",b->id));
  xfree(b->mem);
  xfree(b);
  tref--;
  if(!tref)
  {
    xfree(tmem);
    tmem=NULL;
    tsz=0;
  }
  assert(tref>=0);
  LEAVE();
}

