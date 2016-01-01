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

#include <assert.h>
#include <stdio.h>
#include "memory.h"
#include "list.h"
#include "pipe.h"
#include "buffer.h"
#include "debug.h"

#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL 0
#endif
#define DEBUG_LEVEL 0

#define PIPE_NO_LIMIT (-1)

struct pipe*
pipe_alloc()
{
  struct pipe*p;
  p=(struct pipe*)xcalloc(sizeof(struct pipe));
  return p;
}

void
pipe_init(struct pipe*p,int mode)
{
  static int id=0;
  ENTER();
  assert(xmem(p));
  assert((mode&PIPE_RD)^(mode&PIPE_WR));
  p->next=NULL;
  p->_next=NULL; 
  p->mode=mode;
  p->id=id++;
  p->b=NULL;
  p->i_lim=PIPE_NO_LIMIT;
  DBM(1, printf("pipe_init(p%d,mode %d)\n", p->id, mode ));
  LEAVE();
}

struct pipe*
pipe_new(int mode)
{
  struct pipe*p;
  ENTER();
  DBM(1, printf("pipe_new(ode %d)\n", mode ));
  p=pipe_alloc();
  pipe_init(p,mode);
  LEAVE();
  return p;
}

void
pipe_attach(struct pipe*p,struct buffer*b)
{
  ENTER();
  assert(xmem(p));
  assert(xmem(b));
  assert(p->b==NULL);
  DBM(1, printf("pipe_attach(p%d,b%d)\n", p->id, b->id ));
  p->b=b;
  if(is_reader(p))
    buffer_attach_reader(b,p);
  else
  if(is_writer(p))
    buffer_attach_writer(b,p);
  else
    assert(0);
  pipe_reset(p);
  LEAVE();
}

void
pipe_detach(struct pipe*p)
{
  ENTER();
  assert(xmem(p));
  DBM(1, printf("pipe_detach(p%d,b%d)\n", p->id, p->b->id ));
  if(is_reader(p)) 
    buffer_detach_reader(p->b,p);
  else
  if(is_writer(p))
    buffer_detach_writer(p->b,p);
  else
    assert(0);
  LEAVE();
}

struct pipe*
reader_new(struct buffer*b)
{
  struct pipe*p;
  assert(xmem(b));
  p=pipe_new(PIPE_RD);
  pipe_attach(p,b);
  return p;
}

struct pipe*
writer_new(struct buffer*b)
{
  struct pipe*p;
  assert(xmem(b));
  p=pipe_new(PIPE_WR);
  pipe_attach(p,b);
  return p;
}

int
pipe_invariant(struct pipe*p)
{
  assert(xmem(p));
  int err = 0;
  if(is_reader(p))
  {
    if(p->i < p->b->null) err = -1;
    if(p->i > p->b->offset) err = -2;
  }
  else
  if(is_writer(p))
  {
    if(p->i < p->b->offset) err = -3;
    if(p->i > p->b->offset+p->b->size) err = -4;
  }
  if(p->i_lim >= 0 && p->i > p->i_lim)
  {
    err = -5;
  }
  if (err<0)
  {
    printf( "pipe_invariant err=%d\n", err );
    show_stackframe();
    return 0;
  }
  return buffer_invariant(p->b);
}

void 
pipe_reset(struct pipe*p)
{
  ENTER();
  assert(xmem(p));
  assert(xmem(p->b));
  DBM(1, printf("pipe_reset(p%d)\n", p->id ));
  /*p->done=0;*/
  if(is_reader(p))
    p->i=p->b->null; /* back to start */
  else
  if(is_writer(p))
    p->i=p->b->offset; /* back to start */
  else
    assert(0);
  /*p->request_i=p->i;*/
  assert(pipe_invariant(p));
  LEAVE();
}

#if 0
void 
pipe_flush(struct pipe*p)
{
  ENTER();
  assert(xmem(p));
  assert(xmem(p->b));
  DBM(1, printf("pipe_reset(p%d)\n", p->id ));
  /*p->done=0;*/
  if(is_reader(p))
    p->i=p->b->offset; /* skip to finish */
  else
  if(is_writer(p))
    p->i=p->b->null; /* skip to finish */
  else
    assert(0);
  /*p->request_i=p->i;*/
  assert(pipe_invariant(p));
  LEAVE();
}
#endif

int
pipe_id(struct pipe*p)
{
  assert(xmem(p));
  return p->id;
}

#define PIPE_CHARS_N 256
static char
pipe_chars[PIPE_CHARS_N];
char*
pipe_str(struct pipe*p)
{
  /* KNOW WELL: overwrites previous call */
  assert(xmem(p));
  snprintf(
    pipe_chars,PIPE_CHARS_N,
    "%sp%d;size=%d",
    is_reader(p)?"r":"w",
    p->id, 
    is_reader(p)?read_size(p):write_size(p));
  return pipe_chars;
}

void
pipe_print(struct pipe*p,int indent)
{
  int i;
  assert(xmem(p));
  for(i=indent;i;i--)
    printf("  ");
  printf("pipe #%d %p i=%d i_lim=%d\n",p->id,p, p->i, p->i_lim);
}

/* fatal error */
void
pipe_error(struct pipe*p,char*msg)
{
  char m[256];
  assert(xmem(p));
  snprintf(m,255," !!** pipe_error p%d %p %s ", p->id, p, msg );
  perror(m);
  exit(1);
}

/* non fatal */
void
pipe_msg(struct pipe*p,char*msg)
{
  char m[256];
  assert(xmem(p));
  snprintf(m,255," !!** pipe_msg t%d %p %s ", p->id, p, msg );
  perror(m);
}

#define MAX(a,b) ((a>b)?a:b)
#define MIN(a,b) ((a<b)?a:b)

int
pipe_get_i(struct pipe*p)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  return p->i;
}

unsigned int
read_size(struct pipe*p)
{
  int sz;
  assert(xmem(p));
  assert(pipe_invariant(p));
  assert(is_reader(p));
  sz=buffer_read_size(p->b,p->i);
  if(p->i_lim>=0)
    sz=MIN(sz,p->i_lim-p->i);
  return sz;
}

void
consume(struct pipe*p,int i)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  assert(is_reader(p));
  DBM(1, printf("consume(p%d,%d)\n", p->id, i ));
  p->i+=i;
  /*buffer_send_read(p->b);*/
  assert(pipe_invariant(p));
}

unsigned int
write_size(struct pipe*p)
{
  int sz;
  assert(xmem(p));
  assert(pipe_invariant(p));
  assert(is_writer(p));
  sz=buffer_write_size(p->b,p->i);
  if(p->i_lim>=0)
    sz=MIN(sz,p->i_lim-p->i);
  return sz;
}

void
produce(struct pipe*p,int i)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  assert(is_writer(p));
  DBM(1, printf("produce(p%d,%d)\n", p->id, i ));
  p->i+=i;
  /*buffer_send_write(p->b);*/
  assert(pipe_invariant(p));
}

int
is_reader(struct pipe*p)
{
  assert(xmem(p));
  return p->mode&PIPE_RD;
}

int
is_writer(struct pipe*p)
{
  assert(xmem(p));
  return p->mode&PIPE_WR;
}

void*
reader_mem(struct pipe*p)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  assert(is_reader(p));
  return buffer_peek_read(p->b,p->i);
}

void*
writer_mem(struct pipe*p)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  assert(is_writer(p));
  return buffer_peek_write(p->b,p->i);
}

int
reader_request(struct pipe*p,int size)
{
  assert(xmem(p));
  assert(size>=0);
  if(p->i_lim>=0 && size > p->i_lim-p->i )
  {
    /* pipe_msg(p,"reader_request"); */
    return 0;
  }
  return buffer_request_read(p->b,p->i,size);
}

int
writer_request(struct pipe*p,int size)
{
  assert(xmem(p));
  assert(size>=0);
  if(p->i_lim>=0 && size > p->i_lim-p->i )
  {
    /* pipe_msg(p,"reader_request"); */
    return 0;
  }
  return buffer_request_write(p->b,p->i,size);
}

void
reader_seek(struct pipe*p,int i)
{
  assert(xmem(p));
  assert(is_reader(p));
  p->i=i;
  assert(pipe_invariant(p));
}

void
writer_seek(struct pipe*p,int i)
{
  assert(xmem(p));
  assert(is_writer(p));
  p->i=i;
  assert(pipe_invariant(p));
}

void
pipe_limit(struct pipe*p, int i)
{
  /* stop at i */
  assert(xmem(p));
  p->i_lim=i;
  assert(pipe_invariant(p));
}

int
pipe_get_limit(struct pipe*p)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  return p->i_lim;
}

void
pipe_no_limit(struct pipe*p)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  p->i_lim=PIPE_NO_LIMIT;
}

int
pipe_done(struct pipe*p)
{
  assert(xmem(p));
  assert(pipe_invariant(p));
  return p->i==p->i_lim;
}

#include <string.h>

#define DEBUG_LEVEL 0
/* NB. if buffer overflows we may lose messages. */
int
read_msg(struct pipe*p,char*c,int n)
{
  int sz,i;
  char*rmem;
  assert(xmem(p));
  assert(c);
  assert(n>0);
  n--; /* paranoia */
  sz=read_size(p);
  DBM(2,printf("read_msg(): read_size=%d\n",sz));
  if(sz==0) { return 0; }
  DBM(1,printf("read_msg(): read_size=%d\n",sz));
  rmem=reader_mem(p);
  /* while(sz) */
  for(i=0;i<sz&&i<n;i++)
    if(rmem[i]=='\0') { i++; break; }
  assert(i<n); memcpy(c,rmem,i); c+=i; n-=i;
  consume(p,i);
  assert(i);
  if(rmem[i-1]=='\0')
    return i; /* success */
  /* message split over buffer boundary */
  sz=read_size(p);
    DBM(1,printf("read_msg(): message split, read_size=%d\n",sz));
    if(sz==0)
    {
      /* lost a message ! */
      DBM(0,printf("read_msg(): **** lost a message ****\n"));
      return 0;
    }
  /* continue read */
  rmem=reader_mem(p);
  for(i=0;i<sz&&i<n;i++)
    if(rmem[i]=='\0') { i++; break; }
  assert(i<n); memcpy(c,rmem,i); c+=i; n-=i;
  consume(p,i);
  assert(i);
  if(rmem[i-1]=='\0')
    return 1; /* success */
  /* lost a message ! */
  DBM(0,printf("read_msg(): **** lost a message ****\n"));
  assert(0);
  return 0;
}

/* NB. if buffer overflows we may lose messages. */
int
write_msg(struct pipe*p,char*c)
{
  int sz;
  char*wmem;
  int n;
  assert(xmem(p));
  assert(c);
  n=strlen(c)+1;
  DBM(1,printf("write_msg(%s)\n",c));
  sz=write_size(p);
  DBM(1,printf("write_msg(): write_size=%d\n",sz));
  if(sz==0) { return 0; }
  /* while(n) */
  wmem=writer_mem(p);
  if(sz>=n)
  {
    memcpy(wmem,c,n); produce(p,n);
    return 1;
  } 
  memcpy(wmem,c,sz); c+=sz; n-=sz; produce(p,sz);
  DBM(1,printf("write_msg(): message split\n"));
  sz=write_size(p);
  DBM(1,printf("write_msg(): write_size=%d\n",sz));
  if(sz>=n)
  {
    wmem=writer_mem(p);
    memcpy(wmem,c,n); produce(p,n);
    return 1;
  }
#ifdef DESPARATE
  else
  {
    /* push */
    DBM(1,printf("write_msg(): writer_request(%d)\n",n));
    writer_request(p,n);
    sz=write_size(p);
    DBM(1,printf("write_msg(): write_size=%d\n",sz));
    if(sz>=n)
    {
      wmem=writer_mem(p);
      memcpy(wmem,c,n); produce(p,n);
      return 1;
    }
  }
#endif
  DBM(0,printf("write_msg(): **** lost a message ***\n"));
  assert(0);
  return 0;
}
    
int
__read_msg(struct pipe*p,char*c,int n)
{
  int sz,i;
  char*rmem;
  assert(xmem(p));
  assert(c);
  assert(n>0);
  n--;
  sz=read_size(p);
  DBM(2,printf("read_msg: A: sz=%d\n",sz));
  if(sz==0)
  {
    return 0;
  }

  /* consume WS */
  DBM(1,printf("read_msg: B: sz=%d\n",sz));
  rmem=reader_mem(p);
  for(i=0;i<sz;i++)
    if(rmem[i]!=' ')
      break;
  if(i)
  {
    DBM(1,printf("read_msg: ws=%d\n",i));
    consume(p,i);
    sz=read_size(p);
  }

  /* scan line */
  DBM(1,printf("read_msg: C: sz=%d\n",sz));
  if(sz==0) return 0;
  rmem=reader_mem(p);
  for(i=0;i<sz;i++)
    if(rmem[i]=='\n')
      break;

  if(i==sz) 
  {
    /* try pull */
    DBM(1,printf("read_msg: pulling\n"));
    sz=reader_request(p,sz+1);
    if(sz<=i) return 0;
    rmem=reader_mem(p);
    for(i=0;i<sz;i++)
      if(rmem[i]=='\n')
        break;
    if(i==sz) return 0;
  }

  assert(i<sz);
  assert(rmem[i]=='\n');
  i++;
  if(i>=n)
  {
    DBM(1,printf(" ** read_msg: too big **\n"));
    exit(1);
  }
  memcpy(c,rmem,i);
  consume(p,i);
  c[i]='\0';
  DBM(1,printf("read_msg: '%s'\n",c));
  return i;
}

int
__write_msg(struct pipe*p,char*c)
{
  int sz,len;
  assert(xmem(p));
  sz=write_size(p);
  if(sz==0) return 0;
  len=strlen(c);
  if(len>sz)
  {
#if 1
    {
      /* fill with WS */
      memset(writer_mem(p),' ',sz);
      produce(p,sz);
      sz=write_size(p);
    }
#else
      /* push */
      sz=writer_request(p,len);
#endif
  }
  if(len<=sz)
  {
    DBM(1,printf("write_msg: '%s'\n",c));
    strcpy(writer_mem(p),c);
    produce(p,len);
    return len;
  }
  return 0;
}

void
_writer_nudge(struct pipe*p,int i)
{
  assert(xmem(p));
  assert(is_writer(p));
  DBM(1, printf("_writer_nudge(p%d,%d)\n", p->id,i ));
  p->i+=i;
  assert(pipe_invariant(p));
}

void
_reader_nudge(struct pipe*p,int i)
{
  assert(xmem(p));
  assert(is_reader(p));
  DBM(1, printf("_reader_nudge(p%d,%d)\n", p->id,i ));
  p->i+=i;
  assert(pipe_invariant(p));
}

void 
pipe_free(struct pipe*p)
{
  ENTER();
  assert(xmem(p));
  DBM(1, printf("pipe_free(p%d)\n", p->id ));
  xfree(p);
  LEAVE();
}

