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

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <assert.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
/* #include <limits.h> */
#include <pthread.h> /* mutexes for portaudio */

/* #include <Python.h> */

#include "task.h"
#include "pipe.h"
#include "memory.h"
#include "debug.h"

#include "config.h"

#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL 0
#endif

struct task*
task_alloc()
{
  struct task*t;
  t=(struct task*)xcalloc(sizeof(struct task));
  assert(xmem(t));
  return t;
}

void
task_init(struct task*t,
  void (*reset)(struct task*), 
  unsigned int (*send)(struct task*),
  void (*free)(struct task*))
{
  static int id=0;
  assert(xmem(t));
  ENTER();
  list_init(&t->readers);
  list_init(&t->writers);
  t->reset=reset;
  t->send=send;
  t->free=free;
  t->assert=NULL;
  t->open_reader=NULL;
  t->open_writer=NULL;
  t->close_reader=NULL;
  t->close_writer=NULL;
  t->done=0;
  t->id=id++;
  t->i=0; /* send accumulant */
  t->str=NULL; 
  DBM(1,printf("task_init(t%d)\n",t->id));
  LEAVE();
}

void
task_set_assert(struct task*t,ASSERT a)
{
  t->assert=a;
}

struct task*
task_new(
/*  struct list*owner,*/
/*  void (*reset)(struct task*), */
  unsigned int (*send)(struct task*)
/*  void (*free)(struct task*) */ )
{
  struct task*t;
  ENTER();
  DBM(1,printf("task_new()\n"));
  t=task_alloc();
  assert(xmem(t));
  task_init(t,NULL,send,NULL);
  LEAVE();
  return t;
}

void
task_reset(struct task*t)
{
  assert(xmem(t));
  ENTER();
  list_iterate(&t->readers,(ITER)pipe_reset);
  list_iterate(&t->writers,(ITER)pipe_reset);
  DBM(1,printf("task_reset(t%d)\n",t->id));
  if(t->reset)
    (*t->reset)(t);
  task_set_done(t,0);
  LEAVE();
}

unsigned int
task_send(struct task*t)
{
  ENTER();
  assert(xmem(t));
  if(t->assert) (*t->assert)(t);
  if(t->send && !task_is_done(t))
  {
    int i;
    Py_BEGIN_ALLOW_THREADS
    i=(*t->send)(t);
    Py_END_ALLOW_THREADS
    t->i+=i;
    DBM(2,printf("task_send(t%d): %d\n", t->id, i ));
    if(t->assert) (*t->assert)(t);
    LEAVE();
    return i;
  }
  /*printf("what????\n");*/
  LEAVE();
  return 0;
}

void
task_set_done(struct task*t,int done)
{
  t->done=done;
}

int
task_is_done(struct task*t)
{
  return t->done;
}

void
task_free(struct task*t)
{
  struct pipe*p;
  ENTER();
  assert(xmem(t));
  if(t->assert) (*t->assert)(t);
  DBM(1,printf(">task_free(t%d)\n",t->id);fflush(stdout););
  for(p=reader(t);p;p=reader(t))
    close_reader(t,p);
  for(p=writer(t);p;p=writer(t))
    close_writer(t,p);
  if(t->free)
    (*t->free)(t);
  xfree(t);
  DBM(1,printf("<task_free\n"));
  LEAVE();
}

int
task_id(struct task*t)
{
  assert(xmem(t));
  return t->id;
}

#define TASK_CHARS_N 256
static char
task_chars[TASK_CHARS_N];
char*
task_str(struct task*t)
{
  /* KNOW WELL: overwrites previous call */
  int i;
  struct pipe*p;
  assert(xmem(t));
  i=snprintf(task_chars,TASK_CHARS_N,"t%d;i=%d", t->id, t->i );
  for(p=reader(t);p;p=next_reader(t,p))
    i+=snprintf(task_chars+i,TASK_CHARS_N-i,"{%s}", pipe_str(p));
  for(p=writer(t);p;p=next_writer(t,p))
    i+=snprintf(task_chars+i,TASK_CHARS_N-i,"{%s}", pipe_str(p));
  return task_chars;
}

void
task_print(struct task*t)
{
  assert(xmem(t));
  /* if(t->str) (*t->str)(t,,TASK_CHARS_N); */
  printf("task %s\n", task_str(t));
}

/* fatal error */
void
task_error(struct task*t,char*msg)
{
  char m[256];
  assert(xmem(t));
  snprintf(m,255," !!** task_error t%d %p %s ", t->id, t, msg );
  perror(m);
  exit(1);
}

/* non fatal */
void
task_msg(struct task*t,char*msg)
{
  char m[256];
  assert(xmem(t));
  snprintf(m,255," !!** task_msg t%d %p %s ", t->id, t, msg );
  perror(m);
}

struct pipe*
writer(struct task*t)
{
  assert(xmem(t));
  return list_first(&t->writers);
}

struct pipe*
reader(struct task*t)
{
  assert(xmem(t));
  return list_first(&t->readers);
}

struct pipe*
next_writer(struct task*t,struct pipe*p)
{
  assert(xmem(t));
  assert(is_writer(p));
  return list_next(&t->writers,p);
}

struct pipe*
next_reader(struct task*t,struct pipe*p)
{
  assert(xmem(t));
  assert(is_reader(p));
  return list_next(&t->readers,p);
}

struct pipe*
writer_at(struct task*t,int _i)
{
  struct pipe*wp;
  int i;
  assert(xmem(t));
  wp=writer(t);
  for(i=0;wp && i<_i;i++)
    wp=next_writer(t,wp);
  return wp;
}

struct pipe*
reader_at(struct task*t,int _i)
{
  struct pipe*rp;
  int i;
  assert(xmem(t));
  rp=reader(t);
  for(i=0;rp && i<_i;i++)
    rp=next_reader(t,rp);
  return rp;
}

/* #define DEBUG_LEVEL 1 */
struct pipe*
open_reader(struct task*t,struct buffer*b)
{
  struct pipe*p;
  assert(xmem(t));
  assert(xmem(b));
  ENTER();
  if(t->open_reader)
    p=(*t->open_reader)(t,b); /* chain */
  else
  {
    /* p=pipe_new(PIPE_RD); */
    /* pipe_attach(p,b); */
    p = reader_new(b);
  }
  list_append(&t->readers,p);
  DBM(1,printf("open_reader(t%d,b%d)=p%d\n",t->id,b->id,p->id ));
  LEAVE();
  return p;
}

void
close_reader(struct task*t,struct pipe*p)
{
  ENTER();
  assert(xmem(t));
  assert(xmem(p));
  assert(is_reader(p));
  /*assert(p->t==t);*/
  DBM(1,printf("close_reader(t%d,p%d)\n",t->id,p->id ));
  if(t->close_reader)
    (*t->close_reader)(t,p); /* chain */
  else
    pipe_detach(p);
  list_remove(&t->readers,(LINK)p);
  pipe_free(p);
  LEAVE();
}

struct pipe*
open_writer(struct task*t,struct buffer*b)
{
  struct pipe*p;
  ENTER();
  assert(xmem(t));
  assert(xmem(b));
  DBM(1,printf("open_writer(t%d,b%d)\n",t->id,b->id ));
  if(t->open_writer)
    p=(*t->open_writer)(t,b); /* chain */
  else
  {
    /* p=pipe_new(PIPE_WR); */
    /* pipe_attach(p,b); */
    p = writer_new(b);
  }
  list_append(&t->writers,p);
  DBM(1,printf("open_writer(t%d,b%d)=p%d\n",t->id,b->id,p->id ));
  LEAVE();
  return p;
}

void
close_writer(struct task*t,struct pipe*p)
{
  assert(xmem(t));
  assert(xmem(p));
  assert(is_writer(p));
  /*assert(p->t==t);*/
  ENTER();
  DBM(1,printf("close_writer(t%d,p%d)\n",t->id,p->id ));
  if(t->close_writer)
    (*t->close_writer)(t,p);
  else
    pipe_detach(p);
  list_remove(&t->writers,(LINK)p);
  pipe_free(p);
  LEAVE();
}
/* #define DEBUG_LEVEL 0 */

void
dump_size(struct task*t, char*name)
{
  struct pipe*p;
  printf("dump_size %s : ",name);
  for(p=reader(t);p;p=next_reader(t,p))
    printf(" read=%d ", read_size(p));
  for(p=writer(t);p;p=next_writer(t,p))
    printf(" write=%d ", write_size(p));
  printf("\n");
}
 
/*
 *******************************************************
 */

int
task_read_int(struct task*t)
{
  /* this is not great */
  struct pipe*p;
  p=reader(t);
  if(read_size(p)>=sizeof(int))
  {
    int*i=reader_mem(p);
    consume(p,sizeof(int));
    return *i;
  }
  return 0;
}

/* [input]*-> */
unsigned int
task_null_send(struct task*t)
{
  struct pipe*p;
  int i=0;
  for(p=reader(t);p;p=next_reader(t,p))
  {
    int size;
    size=read_size(p);
    if(size)
    {
      //printf("null: mem=%p, size=%d\n",  reader_mem(p), size );
      consume(p,size);
    }
    i+=size;
  }
  return i;
}
SIMPLE_TASK(null)

/* ->[output]* */
unsigned int
task_zero_send(struct task*t)
{
  struct pipe*p;
  int i=0;
  for(p=writer(t);p;p=next_writer(t,p))
  {
    int size;
    size=write_size(p);
    if(size)
    {
      memset(writer_mem(p),0,size);
      produce(p,size);
      i+=size;
    }
  }
  return i;
}
SIMPLE_TASK(zero)

unsigned int
task_dummy_send(struct task*t)
{
  struct pipe*p;
  int i,count=0;
  assert(xmem(t));
  for(p=reader(t);p;p=next_reader(t,p))
  {
    i=read_size(p); 
    if(i)
      consume(p,i);
    count+=i;
  }
  for(p=writer(t);p;p=next_writer(t,p))
  {
    i=write_size(p);
    if(i)
      produce(p,i);
    count+=i;
  }
  return count;
}
SIMPLE_TASK(dummy)

struct task*
task_none_new()
{
  return task_new(NULL);
}

/*
 ***********************************************************
 */

struct task_skip
{
  struct task t;
  float sk;
  int i;
};

unsigned int
task_skip_send(struct task_skip*t)
{
  unsigned int count=0;
  int rsz,wsz,sz;
  struct pipe*rp,*wp;
  assert(xmem(t));
  ENTER();
  rp=reader((TASK)t);
  wp=writer((TASK)t);
  rsz=read_size(rp); 
  wsz=write_size(wp);
  sz=MIN(rsz,wsz);
  DBM(1,printf("skip rsz=%d, wsz=%d\n",rsz,wsz));
  if(rsz)
  {
    if( floor(t->i / t->sk)-floor((t->i-1) / t->sk) )
    {
      DBM(1,printf("skip: copy\n"));
      if(wsz==0) 
      {
        DBM(1,printf("skip wsz=0\n"));
        LEAVE();
        return 0;
      }
      /* copy */
#if 0
      memcpy(writer_mem(wp),reader_mem(rp),sz);
      consume(rp,sz);
      produce(wp,sz);
      count+=sz;
#endif
      count+=task_copy_send((TASK)t);
      assert(count);
    }
    else
    {
      /* skip */
      DBM(1,printf("skip OK\n"));
      consume(rp,rsz);
      count+=rsz;
    }
    t->i++;
  }
  DBM(1,printf("skip count=%d\n",count));
  LEAVE();
  return count;
}

struct task*
task_skip_new(float sk/*how many blocks to skip between a copy*/)
{
  struct task_skip*t;
  t=(struct task_skip*)xcalloc(sizeof(struct task_skip));
  task_init((TASK)t,NULL,(SEND)task_skip_send,NULL);
  t->sk=sk;
  t->i=0;
  return (TASK)t;
}

/*
 *******************************************************
 */

struct task_mem
{
  struct task t;
  char*mem;  
  int size; /* mem size */
  int offset; /* mem offset */
};

unsigned int
task_mem_wr_send(struct task_mem*t);
unsigned int
task_mem_rd_send(struct task_mem*t);
unsigned int
task_loop_send(struct task_mem*t);

void
task_mem_reset(struct task_mem*t)
{
  t->offset=0;
}

void
task_mem_seek(struct task*_t, int offset)
{
  struct task_mem*t = (struct task_mem*)_t;
  assert(xmem(t));
  if (offset>=t->size)
  {
    task_msg(_t, "task_mem_seek: offset>=t->size" );
    offset = t->size;
    task_set_done((TASK)t,1);
  }
  if (offset<0)
  {
    task_msg(_t, "task_mem_seek: offset<0" );
    offset = 0;
  }
  t->offset = offset;
}

int
task_mem_get_offset(struct task*_t)
{
  struct task_mem*t = (struct task_mem*)_t;
  assert(xmem(t));
  return t->offset;
}

struct task*
task_mem_new(void*mem, int size,SEND send)
{
  struct task_mem*t;
  t=(struct task_mem*)xcalloc(sizeof(struct task_mem));
  task_init((TASK)t,(RESET)task_mem_reset,send,NULL);
  t->mem=(char*)mem;
  t->size=size;
  t->offset=0;
  return (TASK)t;
}

struct task*
task_mem_rd_new(void*mem, int size)
{
  return task_mem_new(mem, size, (SEND)task_mem_rd_send);
}

struct task*
task_mem_wr_new(void*mem, int size)
{
  return task_mem_new(mem, size, (SEND)task_mem_wr_send);
}

struct task*
task_loop_new(void*mem, int size )
{
  return task_mem_new(mem, size, (SEND)task_loop_send);
}

/* ->output */
unsigned int
task_mem_rd_send(struct task_mem*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int _i;
    _i=write_size(p);
    if(_i && t->offset<t->size)
    {
      int size=MIN( t->size-t->offset, _i );
      assert(size>0);
      memcpy(writer_mem(p), t->mem+t->offset, size );
      t->offset+=size;
      produce(p,size);
      i+=size;
      if(t->offset==t->size)
        task_set_done((TASK)t,1);
    }
  }
  return i;
}

/* input-> */
unsigned int
task_mem_wr_send(struct task_mem*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=reader((TASK)t);
  if(p)
  {
    int _i;
    _i=read_size(p);
    if(_i && t->offset<t->size)
    {
      int size=MIN( t->size-t->offset, _i );
      assert(size>0);
      memcpy(t->mem+t->offset, reader_mem(p), size );
      t->offset+=size;
      consume(p,size);
      i+=size;
      if(t->offset==t->size)
        task_set_done((TASK)t,1);
    }
  }
  return i;
}

/* ->output */
unsigned int
task_loop_send(struct task_mem*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int _i;
    _i=write_size(p);
    if(_i)
    {
      int j=0;
      for(;j<_i;)
      {
        int size=MIN( t->size-t->offset , _i-j  );
        assert(size>0);
        /* printf("task_loop_send %p <- %p (%d)\n", */
         /* (char*)writer_mem(p)+j, t->mem+t->offset, size ); */
        memcpy((char*)writer_mem(p)+j, t->mem+t->offset, size );
        j+=size;
        t->offset+=size;
        t->offset%=t->size; /* loop */
      }
      produce(p,_i);
      i+=_i;
    }
  }
  return i;
}

/*
 *******************************************************
 */

#include <fcntl.h>
#include <errno.h>

/* from W.R. Stevens APUE */
void
set_fl(int fd, int flags) /* flags are file status flags to turn on */
{
  int val;
  if ((val = fcntl(fd, F_GETFL, 0)) < 0)
    {perror("fcntl F_GETFL error");exit(1);}
  val |= flags;		/* turn on flags */
  if (fcntl(fd, F_SETFL, val) < 0)
    {perror("fcntl F_SETFL error");exit(1);}
}
/* end from W.R. Stevens APUE */

struct task_fd
{
  struct task t;
  int fd;
  /*unsigned int offset;*/ /* into block */
  int minbytes; /* wait until we can process this many bytes */
  int maxminbytes;
};

void
task_fd_free(struct task_fd*t)
{
  close(t->fd);
  t->fd=-1;
}

void
task_fd_reset(struct task_fd*t)
{
  assert(xmem(t));
  task_fd_seek((TASK)t,0);
}

struct task*
task_fd_new(int fd,int minbytes,SEND send)
{
  struct task_fd*t;
  assert(fd>=0);
  /* printf("task_fd_new(fd=%d)\n",fd); */
  t=(struct task_fd*)xcalloc(sizeof(struct task_fd));
  task_init((TASK)t,(RESET)task_fd_reset,send,(FREE)task_fd_free);
  t->fd=fd;
  assert(minbytes>0); /* need a byte */
  t->minbytes=minbytes; /* this may shrink */
  t->maxminbytes=minbytes;
  /*t->offset=0;*/
  return (TASK)t;
}

unsigned int
task_fd_wr_send(struct task_fd*t);

struct task*
task_fd_wr_new(int fd)
{
  return task_fd_new(fd,8,(SEND)task_fd_wr_send);
}

unsigned int
task_fd_rd_send(struct task_fd*t);

struct task*
task_fd_rd_new(int fd)
{
  return task_fd_new(fd,64,(SEND)task_fd_rd_send);
}

int
task_fd_seek(struct task*t, int offset )
{
  int r;
  assert(xmem(t));
  /* printf("task_fd_seek: t%d to %d\n", t->id, offset ); */
  r=lseek( ((struct task_fd*)t)->fd, offset, SEEK_SET );
  assert(r==offset);
  task_set_done(t,0);
  return r;
}

void
set_nonblock(int fd)
{
  set_fl(fd,O_NONBLOCK);
}

unsigned int
task_readln_send(struct task*t)
{
  struct pipe*p;
  char msg[MSG_LEN];
  p=writer(t);
  if(!p) return 0;
  if(fgets(msg,MSG_LEN,stdin))
  {
    int i=strlen(msg);
    assert(i);
    msg[i-1]='\0';
    if(!write_msg(p,msg))
      return 0;
    return 1;
  }
  return 0;
}

struct task*
task_readln_new()
{
  set_fl(STDIN_FILENO,O_NONBLOCK);
  return task_new(task_readln_send);
}

#ifdef DEPRECATED
#if 0
struct task*
task_writeln_new()
{
/*  set_fl(STDOUT_FILENO,O_NONBLOCK);*/
  return task_fd_wr_new(STDOUT_FILENO);
}
#endif

unsigned int
task_writeln_send(struct task*t)
{
  struct pipe*p;
  int i,count=0;
  char msg[MSG_LEN];
  p=reader(t);
  if(!p) return 0;
  do
  { 
    i=read_msg(p,msg,MSG_LEN);
    if(!i) break;
    count++;
    puts(msg);
  } while(1);
  return count;
}
SIMPLE_TASK(writeln)
#endif /* DEPRECATED */

#if 0
struct task*
task_errln_new()
{
  set_fl(STDERR_FILENO,O_NONBLOCK);
  return task_fd_wr_new(STDERR_FILENO);
}
#endif

struct task*
task_file_rd_new(char*filename)
{
  int fd=open(filename,O_RDONLY);
  if(fd<0)
  {
    printf("can't open %s\n",filename);
    perror("file_read_new");
    //assert(0);
    return NULL;
  }
  return task_fd_rd_new(fd);
}

struct task*
task_file_wr_new(char*filename)
{
  //int fd=open(filename,O_WRONLY|O_CREAT|O_EXCL,0660);
  int fd=open(filename,O_TRUNC|O_CREAT|O_WRONLY,0660);
  if(fd<0)
  {
    printf("can't open %s\n",filename);
    perror("file_wr_new");
    //assert(0);
    return NULL;
  }
  return task_fd_wr_new(fd);
}

unsigned int
task_fd_rdwr_send(struct task_fd*t);

/************ dsp devices **********************/
#ifdef HAVE_OSS
#include <sys/ioctl.h>
#include <sys/soundcard.h>
#endif /* HAVE_OSS */

void
set_vol(int dev, int chn, int vol)
{
#ifdef HAVE_OSS
  static char mixname[]="/dev/mixer   ";
  int fd, devmask, stereodevs;
  int ret;
  if ( vol < 0 || vol > 100 ) {  printf(" vol \n"); return; }
  if(dev==0) mixname[10]=0;
  else snprintf( mixname+10, 2, "%d", dev );
  printf("set_vol: name=%s chn=%d, vol=%d\n", mixname, chn, vol);
  fd=open(mixname,O_RDWR);
  if( fd < 0 ) { perror( "bomb open"); close(fd); return; }
  ret = ioctl(fd, SOUND_MIXER_READ_DEVMASK, &devmask);
  if( ret < 0 ) { perror( "bomb devmask"); close(fd); return; }
  ret = ioctl(fd, SOUND_MIXER_READ_STEREODEVS, &stereodevs );
  if( ret < 0 ) { perror( "bomb stereodevs"); close(fd); return; }
  /* chn = SOUND_MIXER_VOLUME; */
  if((1<<chn) & devmask)
  {
    int left=vol, right=vol;
    int level;

/*
    ret = ioctl(fd, MIXER_READ(chn), &level);
    if( ret < 0 ) { perror( "bomb mixer_read"); close(fd); return; }
    left = level & 0xff;
    right = (level & 0xff00) >> 8;
    printf("set_vol: read: %d %d\n", left, right );
*/

    level = (vol << 8) + vol;
    ret = ioctl(fd, MIXER_WRITE(chn), &level);
    if( ret < 0 ) { perror( "bomb mixer_write"); close(fd); return; }
    left = level & 0xff;
    right = (level & 0xff00) >> 8;
    printf("set_vol: write: %d %d\n", left, right );
  }
  else
  { printf("set_vol: invalid chn \n"); }
  close(fd);
#endif /* HAVE_OSS */
}

#define MAX_DEV 16
#ifdef HAVE_OSS
static char*
get_dspname(int dev)
{
  static char dspname[]="/dev/dsp   ";
  assert(dev>=0);
  assert(dev<MAX_DEV);
  if(dev==0) dspname[8]=0;
  else snprintf( dspname+8, 2, "%d", dev );
  return dspname;
}

static int dspfd[MAX_DEV]=
{-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};
#endif /* HAVE_OSS */

void
set_recsrc(int dev, int chn)
{
#ifdef HAVE_OSS
  int ret;
  int source;
  source=1<<SOUND_MIXER_LINE;
  source=1<<chn;
  assert(dspfd[dev]>=0);
  ret=ioctl(dspfd[dev],SOUND_MIXER_WRITE_RECSRC,&source); 
  if(ret) { printf("WARNING: cannot set recording source\n"); }
#endif /* HAVE_OSS */
}

#ifdef HAVE_OSS
static int
open_dsp(int dev,  int mode, int srate, int stereo )
{
  char*dspname;
  assert(dev>=0);
  assert(dev<MAX_DEV);
  if(dspfd[dev]>=0)
  {
    /*assert(0);*/ /* re-open NOT IMPLEMENTED */
    close(dspfd[dev]);
    dspfd[dev]=-1;
  }
  dspname=get_dspname(dev);
  DBM(1,printf("open_dsp: '%s'\n", dspname ));
  dspfd[dev]=open(dspname,mode);
  if(dspfd[dev]>=0)
  {
    int format=AFMT_S16_LE;
    int ret;
    ret=ioctl(dspfd[dev],SNDCTL_DSP_SETFMT,&format); assert(!ret);
    ret=ioctl(dspfd[dev],SNDCTL_DSP_STEREO,&stereo); assert(!ret);
    ret=ioctl(dspfd[dev],SNDCTL_DSP_SPEED,&srate); assert(!ret);
  }
  else
  {
    perror("open_dsp");
    /* assert(0); */
  }
  return dspfd[dev];
}
#endif /* HAVE_OSS */

void
task_dsp_free( struct task_fd *t)
{
#ifdef HAVE_OSS
  /* need a task_dsp struct */
#endif /* HAVE_OSS */
}

void dsp_rd_free(struct task_fd*t)
{
#ifdef HAVE_OSS
/*
  set_vol(0,SOUND_MIXER_VOLUME,90);
  set_vol(0,SOUND_MIXER_LINE,0);
*/
  task_fd_free(t);
#endif /* HAVE_OSS */
}

struct task*
task_dsp_rd_new(int dev, int srate, int stereo)
{
#ifdef HAVE_OSS
  int fd;
  fd=open_dsp(dev,O_RDONLY, srate, stereo);
/*
  set_vol(0,SOUND_MIXER_VOLUME,0);
  set_vol(0,SOUND_MIXER_LINE,90);
*/
  return task_fd_new(fd,64,(SEND)task_fd_rd_send);
#else
  assert(0);
  return NULL;
#endif /* HAVE_OSS */
}

struct task*
task_dsp_wr_new(int dev, int srate, int stereo)
{
#ifdef HAVE_OSS
  int fd;
  fd=open_dsp(dev,O_WRONLY, srate, stereo);
  return task_fd_new(fd,8,(SEND)task_fd_wr_send);
#else
  assert(0);
  return NULL;
#endif /* HAVE_OSS */
}

struct task*
task_dsp_rdwr_new(int dev, int srate, int stereo)
{
#ifdef HAVE_OSS
  int fd;
  fd=open_dsp(dev,O_RDWR, srate, stereo);
  return task_fd_new(fd,64,(SEND)task_fd_rdwr_send);
#else
  assert(0);
  return NULL;
#endif /* HAVE_OSS */
}

/*
 ***********************************************************
 */


#ifdef HAVE_JOYSTICK

#include <linux/joystick.h>

/* one joystick so far */
struct dynamic
{
  int val;
  int set; /* has been changed */
  struct task*t; /* the listening task */
};

#define MAX_AXIS 4
#define MAX_BUTTON 4
static struct dynamic joy_axis[MAX_AXIS];
static struct dynamic joy_button[MAX_BUTTON];

/* set the dynamics */
unsigned int
task_joy_send(struct task_fd*t)
{
  struct js_event e;
  int count=0;
  assert(xmem(t));
  while(read(t->fd,&e,sizeof(struct js_event))>0) 
  {
#define DEBUG_LEVEL 0
    DBM(1,printf("joy_send: joystick event\n"));
    DBM(1,printf("joy_send: time=%d, value=%hd, type=%hd number=%hd\n",
      e.time, e.value, e.type, e.number ));
    if( e.type & JS_EVENT_AXIS && e.number < MAX_AXIS )
    {
      joy_axis[e.number].val=e.value;
      joy_axis[e.number].set=1;
      count++;
    }
    else
    if( e.type & JS_EVENT_BUTTON )
    {
      joy_button[e.number].val=e.value;
      joy_button[e.number].set=1;
      count++;
    }
  }
  if (errno != EAGAIN)
    task_error((TASK)t,"joy_send");
  return count; 
}

struct task_dynamic
{
  struct task t;
  struct dynamic* d;
  float mul;
  float add;
};

unsigned int
task_dynamic_send(struct task_dynamic*t)
{
  unsigned int count=0;
  if (t->d->set)
  {
    float val;
    struct pipe*wp;
    t->d->set=0;
    val=t->d->val*t->mul+t->add;
    if((wp=writer((TASK)t)))
    {
      char msg[64];
      snprintf(msg,64,"%f",val);
      write_msg(wp,msg);
      count++;
    }
  }
  return count; 
}

void
task_dynamic_free(struct task_dynamic*t)
{
  t->d->t=NULL;
}

struct task*
task_dynamic_new(struct dynamic* d, float mul, float add)
{
  struct task_dynamic*t;
  assert(d);
  t=(struct task_dynamic*)xcalloc(sizeof(struct task_dynamic));
  task_init((TASK)t,NULL,(SEND)task_dynamic_send,(FREE)task_dynamic_free);
  if(d->t!=NULL)
    task_error((TASK)t,"a client exists already");
  t->d=d;
  t->d->t=(TASK)t; /* subscribe */
  t->mul=mul;
  t->add=add;
  return (TASK)t;
}

struct task*
task_axis_new(int n,float min,float max)
{
  struct task*t;
  float mul,add;
  assert(0<=n);
  assert(n<MAX_AXIS);
  mul=(max-min)/(1<<16);
  add=(max+min)/2.0;
  printf("mul=%f,add=%f\n",mul,add);
  t=task_dynamic_new(joy_axis+n,mul,add);
  return t;
}

struct task*
task_button_new(int n)
{
  struct task*t;
  assert(0<=n);
  assert(n<MAX_BUTTON);
  t=task_dynamic_new(joy_button+n,1.0,0.0);
  return t;
}

/* -> axis-1, axis-2, axis-3, axis-4,
   button-1, button-2, button-3, button-4 */ 
unsigned int
_task_joy_send(struct task_fd*t)
{
  struct js_event e;
  /* we only report the last axis event we got */
  int values[MAX_AXIS];
  int set[MAX_AXIS]={0,0,0,0}; /* was this value set ? */
  int i,count=0;
  struct pipe*wp;
  char msg[64];
  assert(xmem(t));
  while(read(t->fd,&e,sizeof(struct js_event))>0) 
  {
#define DEBUG_LEVEL 0 
    DBM(1,printf("joystick event\n"));
    DBM(1,printf("time=%d, value=%hd, type=%hd number=%hd\n",
      e.time, e.value, e.type, e.number ));
    if( e.type & JS_EVENT_AXIS && e.number < MAX_AXIS )
    {
      values[e.number]=e.value;
      set[e.number]=1;
    }
    else
    if( e.type & JS_EVENT_BUTTON )
    {
      if((wp=writer_at((TASK)t,4+e.number)))
      {
        snprintf(msg,64,"%hd",e.value);
        write_msg(wp,msg);
        count++;
      }
    }
  }
  if (errno != EAGAIN)
    task_error((TASK)t,"joy_send");
  for(i=0;i<MAX_AXIS;i++)
    if(set[i] && ((wp=writer_at((TASK)t,i))))
    {
      float fv;
      snprintf(msg,64,"%d",values[i]);
      fv=(float)values[i]/(1<<16)+0.5;
      fv=fv*4+40;
      snprintf(msg,64,"%f",fv);
      write_msg(wp,msg);
      count++;
    }
  return count; 
}

struct task*
task_joy_new(/*int dev*/)
{
  int fd;
  int dev=0; /* one joystick */
  char joyname[]="/dev/js  ";
  assert(dev>=0); assert(dev<16);
  snprintf( joyname+7, 2, "%d", dev );
  printf("joy_new: open '%s'\n",joyname);
  fd=open(joyname,O_RDONLY|O_NONBLOCK);
  if (fd<0) { perror("joy_new"); exit(-1); }
  return task_fd_new(fd,1,(SEND)task_joy_send);
}

#endif /* HAVE_JOYSTICK */

/***************************/

/* #define DEBUG_LEVEL 2 */
/* input-> */
unsigned int
task_fd_wr_send(struct task_fd*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=reader((TASK)t);
  if(p)
  {
    unsigned int rsz;
    rsz=read_size(p);
    if(rsz>=t->minbytes)
    {
      int size, k;
      void*rmem;
      t->minbytes = t->maxminbytes;
      rmem=reader_mem(p);
      for(k=0;rsz;rsz>>=1,k++);
      rsz=1<<(k-1);
      DBM(2,printf("rsz=%d\n",rsz));
      size=write(t->fd, rmem, rsz);
      DBM(2,printf("fd_wr: mem=%p, size=%d\n",  reader_mem(p), size ));
      if(size==-1)
      {
        if(errno==EAGAIN)
          size=0; /* for non-blocking io */
        else
        {
          perror("fd_wr_send");
          printf("fd_wr_send fd=%d, rsz=%d, rmem=%p\n",
            t->fd, rsz, rmem );
          size=0;
        }
      }
      consume(p,size);
      i+=size;
    }
    else
    {
      reader_request(p,t->minbytes);
      t->minbytes /= 2; /* chill out */
      if(t->minbytes==0) t->minbytes=1;
    }
  }
  return i;
}

/* ->output */
unsigned int
task_fd_rd_send(struct task_fd*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
/* #define DEBUG_LEVEL 2 */
  DBM(2,task_print((TASK)t));
  if(p)
  {
    int wsz;
    wsz=write_size(p);
    DBM(2,printf("fd_rd: write_size=%d\n",wsz));
    if(wsz>=t->minbytes)
    {
      int size;
      t->minbytes = t->maxminbytes;
      size=read(t->fd, writer_mem(p), wsz);
      if(size==-1)
      {
        if(errno==EAGAIN)
          size=0; /* for non-blocking io */
        else
        {
          perror("fd_rd_send");
          printf("fd_rd_send fd=%d, wsz=%d, wmem=%p\n",
            t->fd, wsz, writer_mem(p) );
          size=0;
        }
      }
      else
      if(size==0)
      {
        task_set_done((TASK)t,1);
      }
      else
      {
        DBM(2,printf("fd_rd: produce %d\n",size));
        produce(p,size);
        i+=size;
      }
    }
    else
    {
      writer_request(p,t->minbytes);
      t->minbytes /= 2; /* chill out */
      if(t->minbytes==0) t->minbytes=1;
    }
  }
  return i;
}
/* #define DEBUG_LEVEL 0 */

/* input->output */
unsigned int
task_fd_rdwr_send(struct task_fd*t)
{
  int i=0;
  i+=task_fd_rd_send(t);
  i+=task_fd_wr_send(t);
  return i;
}

/*
 ***********************************************************
 */

#ifdef HAVE_PORTAUDIO
#include "portaudio.h"

void
portaudio_check_err(int err)
{
  if( err != paNoError )
  {
    printf( "PortAudio error: %s\n", Pa_GetErrorText( err ) );
    assert(0);
    exit(-1);
  }
}

struct task_portaudio
{
  struct task t;
  int bpf; /* bytes per frame */
  int ichans, ochans, fpb, dev, srate;
  volatile int count;
  PortAudioStream *stream;
  PyObject*cb;
  PyObject*args;
  PyThreadState*ts;
};

int portaudio_cb(
  void *ibuf, void *obuf,
  unsigned long frames,
  PaTimestamp out_time, void *user_data )
{
  struct task_portaudio*t;
  struct pipe*p;
  int bytec;
  t = (struct task_portaudio*)user_data;
  assert(xmem(t));


  bytec = frames*t->bpf;
  assert( ibuf != NULL || obuf != NULL );
  while ( ibuf != NULL || obuf != NULL )
  {
    if( obuf )
    {
      p = reader((TASK)t);
      if( p == NULL ) { }
      else
      if( read_size(p) < bytec ) { }
      else
      {
        memcpy( obuf, reader_mem(p), bytec );
        consume(p, bytec);
        t->count += bytec; /* atomic */
        obuf = NULL; /* done with obuf */
      }
    }

    if(ibuf)
    {
      p = writer((TASK)t);
      if( p == NULL ) { }
      else
      if( write_size(p) < bytec ) { }
      else 
      {
        memcpy( writer_mem(p), ibuf, bytec );
        produce(p, bytec);
        t->count += bytec; /* atomic */
        ibuf = NULL; /* done with ibuf */
      }
    }
    if ( ibuf != NULL || obuf != NULL ) 
    {
      /* run the python callback object */
      PyObject *res;
      /* fprintf(stderr, __FUNCTION__ "() [%s:%d] cb=%p, args=%p\n", __FILE__, __LINE__, t->cb, t->args ); */
PyEval_AcquireLock();  
      /* fprintf(stderr, __FUNCTION__ "() [%s:%d] cb=%p, args=%p\n", __FILE__, __LINE__, t->cb, t->args ); */
PyThreadState_Swap(t->ts); 
      /* fprintf(stderr, __FUNCTION__ "() [%s:%d] cb=%p, args=%p\n", __FILE__, __LINE__, t->cb, t->args ); */
        res = PyObject_CallObject( t->cb, t->args );
        if ( res == NULL )
        {
          /* assert(0); */
          printf("bomb** %p, %p\n", t->cb, t->args );
PyObject_Print(t->cb,stderr,0);
PyThreadState_Swap(NULL); 
PyEval_ReleaseLock();  

          return 0;
        }
        else
          Py_DECREF(res); 
PyThreadState_Swap(NULL); 
      /* fprintf(stderr, __FUNCTION__ "() [%s:%d] cb=%p, args=%p\n", __FILE__, __LINE__, t->cb, t->args ); */
PyEval_ReleaseLock();  
      /* fprintf(stderr, __FUNCTION__ "() [%s:%d] cb=%p, args=%p\n", __FILE__, __LINE__, t->cb, t->args ); */
    }
  } /* while( ibuf != NULL || obuf != NULL ) */
  /* printf( "%s: done\n", __FUNCTION__ ); */

  return 0;
}

void
task_portaudio_free(struct task_portaudio*t)
{
  assert(xmem(t));
  if( t->stream != NULL)
    task_portaudio_stop((struct task*)t);
}
#endif /* HAVE_PORTAUDIO */

struct task*
/* task_portaudio_new( int ichans, int ochans, int fpb, int dev, int srate ) */
/* task_portaudio_new( PyObject*cb, PyObject*args, int ichans, int ochans, int fpb, int dev, int srate ) */
task_portaudio_new( int ichans, int ochans, int fpb, int dev, int srate )
{
#ifdef HAVE_PORTAUDIO
  struct task_portaudio*t;
  static int portaudio_init = 0;

PyEval_InitThreads(); /* hrmmmm.... */

  if(!portaudio_init)
  {
    /* printf("Pa_Initialize()\n");  */
    portaudio_check_err( Pa_Initialize() );
    
    portaudio_init++;
  }

  t=(struct task_portaudio*)xcalloc(sizeof(struct task_portaudio));
  /* task_init((TASK)t,NULL,(SEND)task_portaudio_send,(FREE)task_portaudio_free); */
  task_init((TASK)t,NULL,(SEND)NULL,(FREE)task_portaudio_free);

  /* printf("task.c: task_portaudio_new( ichans = %d, ochans = %d, dev = %d, srate = %d )\n", */
    /* ichans,ochans,dev,srate ); */

  t->ichans = ichans;
  t->ochans = ochans;
  t->fpb = fpb;
  t->dev = dev;
  t->srate = srate;
  t->stream = NULL;
  t->cb = NULL;
  t->args = NULL;
  t->ts = NULL;

  if ( ichans && ochans ) assert( ichans == ochans );

  if ( ichans ) t->bpf = ichans*2;
  if ( ochans ) t->bpf = ochans*2;

  t->count = 0;


  return (TASK)t;

#else /* HAVE_PORTAUDIO */

  assert(0);
  return NULL;
#endif /* HAVE_PORTAUDIO */
}

void
task_portaudio_start( struct task*_t, PyObject*cb, PyObject*args )
{
#ifdef HAVE_PORTAUDIO
  struct task_portaudio*t;
  assert(xmem(_t));
  t = (struct task_portaudio*)_t;
  assert( t->stream == NULL );

  if(!PyCallable_Check(cb))
  {
    assert(0);
  }
  else
  {
    t->cb = cb;
    Py_INCREF(cb);
  }

  if(args != Py_None) 
  {
    if(!PySequence_Check(args))
    {
      assert(0);
    }
    else
    {
      t->args=args;
      Py_INCREF(cb);
    }
  }
  else t->args = NULL;
  /* fprintf(stderr, __FUNCTION__ "() [%s:%d] cb=%p, args=%p\n", __FILE__, __LINE__, t->cb, t->args ); */

  portaudio_check_err(
    Pa_OpenStream(
      &t->stream,

      t->ichans?t->dev:paNoDevice, /* inputDevice */
      t->ichans, /* numInputChannels */
      paInt16,
      NULL,      /* inputDriverInfo */

      t->ochans?t->dev:paNoDevice, /* outputDevice */
      t->ochans, /* numOutputChannels */
      paInt16,
      NULL,      /* outputDriverInfo */

      t->srate,
      t->fpb,    /* framesPerBuffer */
      2,         /* numberOfBuffers */
      paClipOff, /* streamFlags */
      portaudio_cb, /* callBack */
      t          /* userData */
    )
  ); /* starts portaudio thread */

  /* t->interp = Py_NewInterpreter(); */
  /* assert(t->interp != NULL); */

  /* fprintf(stderr, __FUNCTION__ "() [%s:%d]  \n", __FILE__, __LINE__ );  */
  {
    PyInterpreterState * mis;
    PyThreadState * mts;
    mts = PyThreadState_Get();
    assert(mts);
    mis = mts->interp;
    t->ts = PyThreadState_New(mis);
    assert(t->ts);
    /* fprintf(stderr, __FUNCTION__ "() [%s:%d]  \n", __FILE__, __LINE__ );  */
  }

  portaudio_check_err(Pa_StartStream(t->stream));
#endif
}

void
task_portaudio_stop( struct task*_t )
{
#ifdef HAVE_PORTAUDIO
  struct task_portaudio*t;
  assert(xmem(_t));
  t = (struct task_portaudio*)_t;
  assert( t->stream != NULL );
  portaudio_check_err(Pa_StopStream(t->stream)); 
  portaudio_check_err(Pa_CloseStream(t->stream));
/* Py_EndInterpreter(t->interp); */
/* PyEval_AcquireLock(); */

PyThreadState_Swap(NULL);

PyThreadState_Clear(t->ts);

PyThreadState_Delete(t->ts);

/* PyEval_ReleaseLock(); */


  t->stream = NULL;
  t->cb = NULL;
  t->args = NULL;
#endif
}

/*
 ***********************************************************
 */

/* input->[output]+ */
unsigned int
task_copy_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int i=0;
  unsigned int size;
  rp=reader(t);
  if(!rp)
    return 0;
  size=read_size(rp);
  if(!size)
    return 0;
  for(wp=writer(t);wp;wp=next_writer(t,wp))
  {
    unsigned int _size=write_size(wp);
    size=MIN(_size,size);
  }
  if(!size)
    return 0;
  for(wp=writer(t);wp;wp=next_writer(t,wp))
  {
    memcpy(writer_mem(wp),reader_mem(rp),size);
    produce(wp,size);
    i+=size;
  }
  consume(rp,size);
  return i;
}
SIMPLE_TASK(copy)

/* input->[output]+ */
unsigned int
task_keen_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int i=0;
  unsigned int rsize,wsize;
  rp=reader(t); if(!rp) return 0;
  rsize=read_size(rp);
  wp=writer(t); if(!wp) return 0;
  wsize=write_size(wp);
  if(!wsize) return 0;
  if(rsize)
    i+=task_copy_send(t);
  else
    i+=task_zero_send(t);
  return i;
}
SIMPLE_TASK(keen)

/* short */
/* input -> output */
unsigned int
task_invert_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int i=0;
  unsigned int size,_size;
  int _i;
  short*wmem;
  wp=writer(t);
  if(!wp) return 0;
  size=write_size(wp);
  if(!size) return 0;
  rp=reader(t);
  _size=read_size(rp);
  size=MIN(_size,size);
  if(!size) return 0;
  wmem=writer_mem(wp);
  memcpy(wmem,reader_mem(rp),size);
  consume(rp,size);
  for(_i=0;_i<size/2;_i++)
    wmem[_i]=-wmem[_i];
  i+=size;
  produce(wp,size);
  i+=size;
  return i;
}
SIMPLE_TASK(invert)

#define MIX_MAX 128

/* short */
/* input+ -> output */
unsigned int
task_mean_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int count=0, size;
  short *rmem[MIX_MAX],*wmem;
  int i,_i,n;

  wp=writer(t); if(!wp) return 0;
  size=write_size(wp); if(size<2) return 0;
  wmem=writer_mem(wp);
  if(!reader(t))
  {
    count = task_zero_send(t);
    /* printf(" task_mean_send : %d \n", count ); */
    return count;
  }
  n=0;
  for(rp=reader(t);rp;rp=next_reader(t,rp),n++)
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
    assert(n<MIX_MAX);
    if(size<2) return 0;
    rmem[n]=reader_mem(rp);
  }

  for(i=0;i<size/2;i++)
  {
    int sum=0;
    for(_i=0;_i<n;_i++)
      sum+=rmem[_i][i];
    wmem[i]=sum/n;
  }
  for(rp=reader(t);rp;rp=next_reader(t,rp))
    consume(rp,size);
  produce(wp,size);
  /*printf("mean produce %d\n", size );*/
  count+=size;
  return count;
}
SIMPLE_TASK(mean)

unsigned int
task_mix2_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int count=0, size;
  short *rmem[2],*wmem;
  int i,n;

  wp=writer(t); if(!wp) return 0;
  size=write_size(wp); if(size<2) return 0;
  wmem=writer_mem(wp);
  if(!reader(t)) return task_zero_send(t);
  for(n=0,rp=reader(t);rp&&n<2;rp=next_reader(t,rp),n++)
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
    assert(n<MIX_MAX);
    if(size<2) return 0;
    rmem[n]=reader_mem(rp);
  }
  if(n!=2) return 0;
  for(i=0;i<size/2;i++)
  {
    wmem[i]=(short)((
      (int)rmem[0][i]+(int)rmem[1][i]
    )>>1);
  }
  for(rp=reader(t);rp;rp=next_reader(t,rp)) consume(rp,size);
  produce(wp,size);
  /*printf("mix2 produce %d\n", size );*/
  count+=size;
  return count;
}
SIMPLE_TASK(mix2)

unsigned int
task_mix4_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int count=0, size;
  short *rmem[4],*wmem;
  int i,n;

  wp=writer(t); if(!wp) return 0;
  size=write_size(wp); if(size<2) return 0;
  wmem=writer_mem(wp);
  if(!reader(t)) return task_zero_send(t);
  for(n=0,rp=reader(t);rp&&n<4;rp=next_reader(t,rp),n++)
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
    assert(n<MIX_MAX);
    if(size<2) return 0;
    rmem[n]=reader_mem(rp);
  }
  if(n!=4) return 0;
  for(i=0;i<size/2;i++)
  {
    wmem[i]=(short)((
      (int)rmem[0][i]+(int)rmem[1][i]+
      (int)rmem[2][i]+(int)rmem[3][i]
    )>>2);
  }
  for(rp=reader(t);rp;rp=next_reader(t,rp)) consume(rp,size);
  produce(wp,size);
  /*printf("mix4 produce %d\n", size );*/
  count+=size;
  return count;
}
SIMPLE_TASK(mix4)

unsigned int
task_mix8_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int count=0, size;
  short *rmem[8],*wmem;
  int i,n;

  wp=writer(t); if(!wp) return 0;
  size=write_size(wp); if(size<2) return 0;
  wmem=writer_mem(wp);
  if(!reader(t)) return task_zero_send(t);
  for(n=0,rp=reader(t);rp&&n<8;rp=next_reader(t,rp),n++)
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
    assert(n<MIX_MAX);
    if(size<2) return 0;
    rmem[n]=reader_mem(rp);
  }
  if(n!=8) return 0;
  for(i=0;i<size/2;i++)
  {
    wmem[i]=(short)((
      (int)rmem[0][i]+(int)rmem[1][i]+
      (int)rmem[2][i]+(int)rmem[3][i]+
      (int)rmem[4][i]+(int)rmem[5][i]+
      (int)rmem[6][i]+(int)rmem[7][i]
    )>>3);
  }
  for(rp=reader(t);rp;rp=next_reader(t,rp)) consume(rp,size);
  produce(wp,size);
  /*printf("mix8 produce %d\n", size );*/
  count+=size;
  return count;
}
SIMPLE_TASK(mix8)

/* short */
/* input+ -> output */
unsigned int
task_add_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int i=0;
  unsigned int size;
  wp=writer(t);
  if(!wp) return 0;
  size=write_size(wp);
  if(!size) return 0;
  if(!reader(t))
    return task_zero_send(t); /* add nothing to get zero */
  for(rp=reader(t);rp;rp=next_reader(t,rp))
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
  }
  if(!size) return 0;
  rp=reader(t);
  if(!rp) return 0;
  memcpy(writer_mem(wp),reader_mem(rp),size);
  consume(rp,size);
  i+=size;
  for(rp=next_reader(t,rp);rp;rp=next_reader(t,rp))
  {
    int _i;
    short*wmem=writer_mem(wp),*rmem=reader_mem(rp);
    for(_i=0;_i<size/2;_i++)
      wmem[_i]+=rmem[_i];
    consume(rp,size);
    i+=size;
  }
  produce(wp,size);
  i+=size;
  return i;
}
SIMPLE_TASK(add)

/* short */
/* input+ -> output */
unsigned int
task_rmod_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int i=0;
  unsigned int size;
  wp=writer(t);
  if(!wp) return 0;
  size=write_size(wp);
  if(!size) return 0;
  for(rp=reader(t);rp;rp=next_reader(t,rp))
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
  }
  if(!size) return 0;
  rp=reader(t);
  if(!rp) return 0;
  memcpy(writer_mem(wp),reader_mem(rp),size);
  consume(rp,size);
  i+=size;
  for(rp=next_reader(t,rp);rp;rp=next_reader(t,rp))
  {
    int _i;
    short*wmem=writer_mem(wp),*rmem=reader_mem(rp);
    for(_i=0;_i<size/2;_i++)
    {
      int x=(int)wmem[_i]*(int)rmem[_i];
      wmem[_i]=x>>15;
    }
    consume(rp,size);
    i+=size;
  }
  produce(wp,size);
  i+=size;
  return i;
}
SIMPLE_TASK(rmod)

/* short */
/* input+ -> output */
unsigned int
task_rmod8_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int i=0;
  unsigned int size;
  wp=writer(t);
  if(!wp) return 0;
  size=write_size(wp);
  if(!size) return 0;
  for(rp=reader(t);rp;rp=next_reader(t,rp))
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
  }
  if(!size) return 0;
  rp=reader(t);
  if(!rp) return 0;
  memcpy(writer_mem(wp),reader_mem(rp),size);
  consume(rp,size);
  i+=size;
  for(rp=next_reader(t,rp);rp;rp=next_reader(t,rp))
  {
    int _i;
    short*wmem=writer_mem(wp),*rmem=reader_mem(rp);
    for(_i=0;_i<size/2;_i++)
    {
      int x=(int)wmem[_i]*(int)rmem[_i];
      wmem[_i]=x>>8;
    }
    consume(rp,size);
    i+=size;
  }
  produce(wp,size);
  i+=size;
  return i;
}
SIMPLE_TASK(rmod8)

unsigned int
task_cat_send(struct task*t)
{
  /* meeooow */
  return 0;
}
SIMPLE_TASK(cat)

unsigned int
task_abs_send(struct task*t)
{
  unsigned int count=0;
  struct pipe*wp,*rp;
  short*rmem,*wmem;
  int size,i;
  assert(xmem(t));
  rp=reader((TASK)t);
  wp=writer((TASK)t);
  if(!rp||!wp) return 0;
  size=MIN(read_size(rp),write_size(wp))/2;
  if(!size) return 0;
  rmem=reader_mem(rp);
  wmem=writer_mem(wp);
  for(i=0;i<size;i++)
    wmem[i]=abs(rmem[i]);
  consume(rp,size*2);
  produce(wp,size*2);
  count+=size*2;
  return count;
}
SIMPLE_TASK(abs)

/*
 ***********************************************************
 */

struct task_mix
{
  struct task t;
  float r;
};

/* short */
/* input+ -> output */
unsigned int
task_mix_send(struct task_mix*t)
{
  struct pipe*wp,*rp;
  unsigned int count=0, size;
#define MIX_MAX 128
  short *rmem[MIX_MAX],*wmem;
  int i,_i,n;

  wp=writer((TASK)t); if(!wp) return 0;
  size=write_size(wp); if(size<2) return 0;
  wmem=writer_mem(wp);
  if(!reader((TASK)t))
  {
    count = task_zero_send((TASK)t);
    /* printf(" task_mix_send : %d \n", count ); */
    return count;
  }
  n=0;
  for(rp=reader((TASK)t);rp;rp=next_reader((TASK)t,rp),n++)
  {
    unsigned int _size=read_size(rp);
    size=MIN(_size,size);
    if(size<2) return 0;
    assert(n<MIX_MAX);
    rmem[n]=reader_mem(rp);
  }

  for(i=0;i<size/2;i++)
  {
    int sum=0;
    for(_i=0;_i<n;_i++)
      sum+=rmem[_i][i];
    wmem[i]=sum*t->r;
  }
  for(rp=reader((TASK)t);rp;rp=next_reader((TASK)t,rp))
    consume(rp,size);
  produce(wp,size);
  /*printf("mix produce %d\n", size );*/
  count+=size;
  return count;
}

void
task_mix_free(struct task_mix*t)
{
  assert(xmem(t));
}

struct task*
task_mix_new(float r)
{
  struct task_mix*t;
  t=(struct task_mix*)xcalloc(sizeof(struct task_mix));
  task_init((TASK)t,NULL,(SEND)task_mix_send,(FREE)task_mix_free);
  t->r=r;
  return (TASK)t;
}

void
task_mix_set_r(struct task*t,float r)
{
  ((struct task_mix*)t)->r=r;
}

/*
 ***********************************************************
 */

struct task_gain
{
  struct task t;
  float r;
};

unsigned int
task_gain_send(struct task_gain*t)
{
  unsigned int count=0;
  struct pipe*wp,*rp;
  short*rmem,*wmem;
  int size,i;
  assert(xmem(t));
  rp=reader((TASK)t);
  wp=writer((TASK)t);
  if(!rp||!wp) return 0;
  size=MIN(read_size(rp),write_size(wp))/2;
  if(!size) return 0;
  rmem=reader_mem(rp);
  wmem=writer_mem(wp);
  for(i=0;i<size;i++)
    wmem[i]=(short)(rmem[i]*t->r);
  consume(rp,size*2);
  produce(wp,size*2);
  count+=size*2;
  return count;
}

struct task*
task_gain_new(float r)
{
  struct task_gain*t;
  t=(struct task_gain*)xcalloc(sizeof(struct task_gain));
  task_init((TASK)t,NULL,(SEND)task_gain_send,NULL);
  t->r=r;
  return (TASK)t;
}

void
task_gain_set_r(struct task*t,float r)
{
  ((struct task_gain*)t)->r=r;
}

/*
 ***********************************************************
 */

struct task_delay
{
  struct task t;
  struct buffer*b;
  int n;
  int _n; /* goal */
  int sz; /* == b->sz; */
  struct pipe*rp,*wp;
/*  struct task*in,*out; */
};

unsigned int
task_delay_send(struct task_delay*t)
{
  struct pipe*rp,*wp;
  int isize,osize;
  int count=0;
  assert(xmem(t));

  assert(xmem(t->wp));
  assert(xmem(t->rp));
  
  if(t->n!=t->_n)
  {
    int sz;
    /* printf("task_delay_send: update n-_n=%d",t->n-t->_n);  */
    if(t->n>t->_n)
    {
      sz=MIN(read_size(t->rp),t->n-t->_n);
      /* sz=MIN(sz,128); */
      sz=sz&~1;
      consume(t->rp,sz);
      /* t->_n+=sz; */
      t->n-=sz;
      count+=sz;
    }
    else
    {
      sz=MIN(write_size(t->wp),t->_n-t->n);
      /* sz=MIN(sz,128); */
      sz=sz&~1;
      if(sz)
      {
        memset( writer_mem(t->wp), 0, sz );
        produce(t->wp,sz); /* produce what ? */
        /* t->_n-=sz; */
        t->n+=sz;
        count+=sz;
      }
    }
    /* printf(" post: n-_n=%d\n",t->n-t->_n);  */
    buffer_send(t->b);
  }

  wp=writer((TASK)t);
  if(!wp) return 0;
  rp=reader((TASK)t);
  if(!rp) return 0;
  isize=MIN( read_size(rp), write_size(t->wp) );
  DBM(1,printf("delay read_size(rp)=%d\n",read_size(rp)));
  DBM(1,printf("delay write_size(t->wp)=%d\n",write_size(t->wp)));
  osize=MIN( read_size(t->rp), write_size(wp) );
  DBM(1,printf("delay read_size(t->rp)=%d\n",read_size(t->rp)));
  DBM(1,printf("delay write_size(wp)=%d\n",write_size(wp)));
  DBM(1,printf("delay: isize=%d, osize=%d\n",isize,osize));

  if(isize)
  {
    memcpy(writer_mem(t->wp),reader_mem(rp),isize);
    consume(rp,isize);
    produce(t->wp,isize);
    count+=isize;
  }
  if(osize)
  {
    memcpy(writer_mem(wp),reader_mem(t->rp),osize);
    consume(t->rp,osize);
    produce(wp,osize);
    count+=osize;
  }
  buffer_send(t->b);

  return count;
}

void
task_delay_assert(struct task_delay*t)
{
  assert(xmem(t));
  assert(xmem(t->wp));
  assert(xmem(t->rp));
  assert(xmem(t->b));
}

void
task_delay_free(struct task_delay*t)
{
  assert(xmem(t));
  assert(xmem(t->wp));
  assert(xmem(t->rp));
  pipe_detach(t->wp);
  pipe_free(t->wp);
  pipe_detach(t->rp);
  pipe_free(t->rp);
  assert(xmem(t->b));
  buffer_free(t->b);
}

struct task*
task_delay_new(int n)
{
  struct task_delay*t;
  int sz;
  /* WARNING: n is a byte count, not a sample count! */
  assert(n>=0);
  t=(struct task_delay*)xcalloc(sizeof(struct task_delay));
  task_init((TASK)t,NULL,(SEND)task_delay_send,(FREE)task_delay_free);
  task_set_assert((TASK)t,(ASSERT)task_delay_assert);

  for(sz=4096;sz<n;sz+=4096);
  t->b=buffer_new(sz);
  t->sz=sz;

  t->wp=pipe_new(PIPE_WR); pipe_attach(t->wp,t->b);
  t->rp=pipe_new(PIPE_RD); pipe_attach(t->rp,t->b);

  /*t->wp=open_writer((TASK)t,t->b);*/
  /*t->rp=open_reader((TASK)t,t->b);*/
  assert(write_size(t->wp)>=n);
  memset(writer_mem(t->wp),0,n);
  produce(t->wp,n);
  buffer_send(t->b);

  t->n=n;
  t->_n=n;
  DBM(1,printf("task_delay_new: t->n=%d, t->sz=%d\n",t->n,t->sz));
  return (TASK)t;
}

void
task_delay_set_n(struct task*_t,int _n)
{
  struct task_delay*t;
  t=(struct task_delay*)_t;
  assert(xmem(t));
  t->_n=_n;
  assert(t->_n<=t->sz);
}

void
task_delay_slow_set_n(int n,int dn)
{
}

/*
 ***********************************************************
 */

unsigned int
task_print_short_send(struct task*t)
{
  struct pipe*rp;
  int i,sz;
  short *rmem;
  rp=reader(t);
  if(!rp) return 0;
  if (!(sz=read_size(rp)/2)) return 0;
  rmem=reader_mem(rp);
  for(i=0;i<sz;i++)
    printf("%hd\n", rmem[i] );
  consume(rp,i*2);
  return i*2;
}
SIMPLE_TASK(print_short)

/*
 ***********************************************************
 */

/* char8 -> short16 */
unsigned int
task_8b16_send(struct task*t)
{
  struct pipe*wp,*rp;
  unsigned int i=0;
  unsigned int size;
  unsigned char*rmem;
  short*wmem;

  wp=writer(t);
  if(!wp) return 0;
  rp=reader(t);
  if(!rp) return 0;
  size=MIN(read_size(rp),write_size(wp)/2);
  if(!size) return 0;
  wmem=writer_mem(wp);
  rmem=reader_mem(rp);
  for(i=0;i<size;i++)
    wmem[i]=rmem[i]<<6;
  consume(rp,size);
  produce(wp,size*2);
  return size;
}
SIMPLE_TASK(8b16)


/*
 ***********************************************************
 */

/* stereo -> mono, mono */
/* (short a)*(short b) -> (short a)+(short b) */
unsigned int
task_split_send(struct task*t)
{
  unsigned int count=0;
  struct pipe*wp1,*wp2,*rp;
  short*rmem,*wmem1,*wmem2;
  //int in, out, isize,osize;
  rp=reader(t); if(!rp) return 0;
  wp1=writer(t); if(!wp1) return 0;
  wp2=next_writer(t,wp1); if(!wp2) return 0;
#if 0
  osize=MIN(write_size(wp1),write_size(wp2))/2;
  isize=read_size(rp)/2;
  //dump_size(t,"split");
  if(osize<1||isize<2) return 0;
  rmem=reader_mem(rp);
  wmem1=writer_mem(wp1);
  wmem2=writer_mem(wp2);
  for(in=0, out=0; in+1<isize && out<osize; in+=2, out++ )
  {
    wmem1[out]=rmem[in];
    wmem2[out]=rmem[in+1];
  }
  consume(rp,in*2);
  produce(wp1,out*2);
  produce(wp2,out*2);
  count+=in;
#endif
  while(write_size(wp1)>1 && write_size(wp2)>1 && read_size(rp)>3)
  {
    rmem=reader_mem(rp);
    wmem1=writer_mem(wp1);
    wmem2=writer_mem(wp2);
    wmem1[0]=rmem[0];
    wmem2[0]=rmem[1];
    consume(rp,4);
    produce(wp1,2);
    produce(wp2,2);
    count+=2;
  }
  return count;
}
SIMPLE_TASK(split)

/* stereo to mono */
/* (short a)*(short b) -> (short (a+b)/2) */
unsigned int
task_merge_send(struct task*t)
{
  unsigned int count=0;
  unsigned int size;
  struct pipe*wp,*rp;
  short*rmem,*wmem,i;
  rp=reader(t);
  if(!rp)return 0;
  wp=writer(t);
  if(!wp)return 0;
  size=MIN(2*write_size(wp),read_size(rp));
  if(size<4)return 0;
  rmem=reader_mem(rp);
  wmem=writer_mem(wp);
  for(i=0;i+1<size/2;i+=2)
    wmem[i/2]=((int)rmem[i]+(int)rmem[i+1])/2;
  consume(rp,i);
  produce(wp,i/2);
  count+=i;
  return count;
}
SIMPLE_TASK(merge)

/* (short a)+(short b) -> (short a)*(short b) */
unsigned int
task_interleave_send(struct task*t)
{
  unsigned int count=0;
  unsigned int size;
  struct pipe*wp,*rp1,*rp2;
  short*rmem1,*rmem2,*wmem;
  int i;
  rp1=reader(t); if(!rp1) return 0;
  rp2=next_reader(t,rp1); if(!rp2) return 0;
  wp=writer(t); if(!wp) return 0;

  size=MIN(write_size(wp)/2,read_size(rp1));
  size=MIN(size,read_size(rp2));
  if(size<2) return 0;
  rmem1=reader_mem(rp1);
  rmem2=reader_mem(rp2);
  wmem=writer_mem(wp);
  size/=2;
  for(i=0;i<size;i++)
  {
    wmem[2*i]=rmem1[i];
    wmem[2*i+1]=rmem2[i];
  }
  i*=2;
  consume(rp1,i);
  consume(rp2,i);
  produce(wp,i*2);
  count+=i;
  return count;
}
SIMPLE_TASK(interleave)

/*
 ***********************************************************
 */

struct task_usleep
{
  struct task t;
  int usec;
};

unsigned int
task_usleep_send(struct task_usleep*t);

struct task*
task_usleep_new( int usec )
{
  struct task_usleep*t;
  t=(struct task_usleep*)xcalloc(sizeof(struct task_usleep));
  task_init((TASK)t,NULL,(SEND)task_usleep_send,NULL);
  t->usec=usec;
  return (TASK)t;
}

unsigned int
task_usleep_send(struct task_usleep*t)
{
  unsigned int count=0;
  usleep(t->usec);
  return ++count;
}

int srate=44100;
#define SRATE srate

/*
 ***********************************************************
 */

struct task_snatch
{
  struct task t;
  float f;
  int n; /* 1/4 wave len */
  /*int i;*/ /* leftover ? */
  char fmt[MSG_LEN];
};

/* short |
         V
        "float" */

unsigned int
task_snatch_send(struct task_snatch*t)
{
  unsigned int count=0;
  struct pipe*rp,*wp;
  short*rmem;
  int sz;
  assert(xmem(t));

  rp=reader((TASK)t);
  if(!rp) return 0;
  sz=read_size(rp)/2;
  if(3*t->n>=sz) return 0;
  wp=writer((TASK)t);
  if(!wp) return 0;
  if(write_size(wp)==0) return 0;

  DBM(1,printf("snatch: sz=%d\n",sz));
  rmem=reader_mem(rp);
  {
    int i,j;
    float re=0.0, im=0.0;
    float r;
    char msg[MSG_LEN];
    int ret;
    for(i=j=0;i+3*t->n<sz;j++)
    {
      re+=rmem[i]; i+=t->n;
      im+=rmem[i]; i+=t->n;
      re-=rmem[i]; i+=t->n;
      im-=rmem[i]; i+=t->n;
    }
    re/=j*2; im/=j*2; /* normalize */
    r=sqrt(im*im+re*re); /* amplitude */
    r/=1<<14;
    ret=snprintf(msg,MSG_LEN,t->fmt,r);
    assert(ret>0);
    if(write_msg(wp,msg))
    {
      DBM(1,printf("snatch consume %d\n",sz*2));
      consume(rp,sz*2);
      count+=sz*2;
    }
    else
      DBM(1,printf("snatch: blocked\n"));
  }
  return count;
}

void
task_snatch_free(struct task_snatch*t)
{
}

void
task_snatch_set_f(struct task*_t,float f)
{
  struct task_snatch*t=(struct task_snatch*)_t;
  t->f=f;
  t->n=(int)floor(SRATE/(4*f));
  if(t->n<2) {assert(0);}
}

struct task*
task_snatch_new(float f,char*fmt)
{
  struct task_snatch*t;
  t=(struct task_snatch*)xcalloc(sizeof(struct task_snatch));
  task_init((TASK)t,NULL,(SEND)task_snatch_send,(FREE)task_snatch_free);
  task_snatch_set_f((TASK)t,f);
  {
    int i;
    for(i=0;fmt[i]!='\0'&&i<MSG_LEN;i++)
      t->fmt[i]=fmt[i];
    assert(i<MSG_LEN);
    /*t->fmt[i++]='\n';*/
    t->fmt[i++]='\0';
  }
  /*strncpy(t->fmt,fmt,MSG_LEN);*/
  return (TASK)t;
}

/*
 ***********************************************************
 */

struct task_find
{
  struct task t;
};

#define PITCH(level)		(1<<(level))
#define IDX_INIT(pitch)		((pitch)-1)
#define IDX_RANGE(i,pitch,len)	((i)+2*(pitch)<(len))
#define IDX_INC(pitch)		(2*(pitch))

#ifdef DEFINED_BUT_NOT_USED
static void
print_mem(short*mem,int len)
{
  int i;
  printf("{");
  for(i=0;i<len;i++)
    printf("%d,",mem[i]);
  printf("}\n");
}
#endif

static void
_xup(short*mem,int level/*present*/,int len)
{
  int i;
  int pitch;
  assert(mem);
  assert(level>=0);
  /* printf("xup -> "); print_mem(mem,len); printf("\n"); */
  /* for(i=IDX_INIT(pitch);IDX_RANGE(i,pitch,len);i+=IDX_INC(pitch)) */
  pitch=PITCH(level);
  for(i=pitch-1;i+2*pitch<len;i+=2*pitch)
  {
    int x=(int)mem[i]+((int)mem[i+pitch]<<1)+(int)mem[i+2*pitch];
#ifdef NO_SHIFT
    mem[i+pitch]=x; /* overflow */
#else
    mem[i+pitch]=x>>2;
#endif
  }
  /* printf("xup <- "); print_mem(mem,len); printf("\n"); */
}

#ifdef DEFINED_BUT_NOT_USED
static void
_xzo(short*mem,int level/*present*/,int len)
{
  int i;
  int pitch;
  assert(mem);
  assert(level>=0);
  pitch=PITCH(level);
  for(i=pitch-1;i+2*pitch<len;i+=2*pitch)
    mem[i+pitch]=0;
}
#endif

static void
_xout(short*mem/*target*/,short*_mem/*source*/,int level,int len)
{
  int i,j;
  int pitch;
  assert(mem);
  assert(level>=0);
  pitch=PITCH(level);
  j=0;
  for(i=pitch-1;i<len;i+=pitch)
    mem[j++]=_mem[i];
  /* printf("%d,%d\n",j,len/(1<<level)); */
  assert(j==len/(1<<level));
}

#ifdef DEFINED_BUT_NOT_USED
static void
_xdn(short*mem,int level/*present*/,int len)
{
  int i;
  int pitch;
  assert(mem);
  level--; /*target*/
  assert(level>=0);
  pitch=PITCH(level);
  /* printf("xdn -> "); print_mem(mem,len); */
  /* for(i=IDX_INIT(pitch);IDX_RANGE(i,pitch,len);i+=IDX_INC(pitch)) */
  for(i=pitch-1;i+2*pitch<len;i+=2*pitch)
  {
    int x;
#ifdef NO_SHIFT
    x=-(int)mem[i]+(int)mem[i+pitch]-(int)mem[i+2*pitch];
#else
    x=-(int)mem[i]+((int)mem[i+pitch]<<2)-(int)mem[i+2*pitch];
#endif
    mem[i+pitch]=x>>1;
  }
  /* printf("xdn <- "); print_mem(mem,len); */
}
#endif

#ifdef DEFINED_BUT_NOT_USED
static int
_error(short*mem,short*_mem,int len)
{
  int e=0,i;
  for(i=0;i<len;i++)
    if(mem[i]>_mem[i])
    {
      e+=mem[i]-_mem[i];
      assert(i&1); 
      /* printf("%d;",i); */
      /* printf("%d;",mem[i]-_mem[i]); */
    }
    else
    if(mem[i]<_mem[i])
    {
      e+=_mem[i]-mem[i];
      assert(i&1); 
      /* printf("%d;",i); */
      /* printf("%d;",_mem[i]-mem[i]); */
    }
  /* printf("\te=%d",e);  */
  /* printf("\n");  */
  return e;
}
#endif

#ifdef DEFINED_BUT_NOT_USED
static void
_xtest(short*mem,short*_mem,int len)
{
  int level;
  memcpy(_mem,mem,len*2);
  for(level=0;level<1;level++)  
    _xup(_mem,level,len);
  /* _error(mem,_mem,len); */
  printf("e=%d\t",_error(mem,_mem,len)); 
  for(;level;level--) 
    _xdn(_mem,level,len); 
  /* _error(mem,_mem,len); */
  printf("e=%d\t",_error(mem,_mem,len)); 
  memcpy(mem,_mem,len*2);
  for(level=0;level<1;level++)  
    _xup(_mem,level,len);
  /* _error(mem,_mem,len); */
  printf("e=%d\t",_error(mem,_mem,len)); 
  for(;level;level--) 
    _xdn(_mem,level,len); 
  /* _error(mem,_mem,len); */
  printf("e=%d\t",_error(mem,_mem,len)); 
    /* _xzo(_mem,level,len);  */
  /* printf("e=%d\t",_error(mem,_mem,len)); */
  printf("\n");
  /* pitch=PITCH(level); */
  /* for(i=IDX_INIT(pitch);IDX_RANGE(i,pitch,len);i+= */
}
#endif

/* #define DEBUG_LEVEL 1 */
unsigned int
task_find_send(struct task_find*t)
{
  struct pipe*rp,*wp;
  short*rmem,*wmem;
  int rsz,wsz;
  int level, pitch;
#define FLEN 1024
#define LEVELS 	7
#define OLEN 	(FLEN/(1<<LEVELS))
  assert(xmem(t));

  rp=reader((TASK)t);
  if(!rp) return 0;
  rsz=read_size(rp)/2;
  wp=writer((TASK)t);
  if(!wp) return 0;
  wsz=write_size(wp)/2;
  DBM(2,printf("find: rsz=%d wsz=%d\n",rsz,wsz));
  if(rsz<FLEN) {reader_request(rp,FLEN*2); return 0; }
  if(wsz<OLEN) {writer_request(wp,OLEN*2); return 0; }

  rmem=reader_mem(rp);
  wmem=writer_mem(wp);
  {
    short mem[FLEN];
    /* short _mem[OLEN]; */
    /* int i; */
    memcpy(mem,rmem,FLEN*2); 
#if 0
    for(i=0;i<FLEN;i++)
    {
#ifdef SQUARE_IT
      int x;
      x=rmem[i]*rmem[i]; 
      mem[i]=x>>15; 
#else /* use ABS */
      mem[i]=abs(rmem[i]);
      /* if(rmem[i]>=0) assert(rmem[i]==mem[i]); */
#endif
    }
#endif
    /* _xtest(mem,_mem,FLEN); */
    for(level=0;level<LEVELS;level++)
      _xup(mem,level,FLEN);
    _xout(wmem,mem,level,FLEN);
    /* print_mem(wmem,OLEN);  */
  }
  pitch=1<<level;
  consume(rp,FLEN*2-2*(pitch - 1));
  produce(wp,2*FLEN/pitch);

  return 1;
}

void
task_find_free(struct task_find*t)
{
}

struct task*
task_find_new()
{
  struct task_find*t;
  t=(struct task_find*)xcalloc(sizeof(struct task_find));
  task_init((TASK)t,NULL,(SEND)task_find_send,(FREE)task_find_free);
  return (TASK)t;
}

/*
 ***********************************************************
 */

/* mean abs */
unsigned int
task_amp_send(struct task*t)
{
  unsigned int count=0;
  struct pipe*rp,*wp;
  short*rmem;
  int sz;
  assert(xmem(t));

  rp=reader((TASK)t);
  if(!rp) return 0;
  sz=read_size(rp)/2;
  if(sz==0) return 0;
  wp=writer((TASK)t);
  if(!wp) return 0;
  if(write_size(wp)<2) return 0;

  DBM(1,printf("amp: sz=%d\n",sz));
  rmem=reader_mem(rp);
  {
    int i;
    float r=0.0;
    /* char msg[32]; */
    for(i=0;i<sz;i++)
      r+=fabs((float)rmem[i]);
    r/=sz; /* average */
    ((short*)writer_mem(wp))[0]=(short)r;
    produce(wp,2);
    consume(rp,sz*2);
  }
  return count;
}
SIMPLE_TASK(amp)

/* #define DEBUG_LEVEL 0 */

/* max abs */
unsigned int
task_env_send(struct task*t)
{
  unsigned int count=0;
  struct pipe*rp,*wp;
  short*rmem;
  int sz;
  assert(xmem(t));

  rp=reader((TASK)t);
  if(!rp) return 0;
  sz=read_size(rp)/2;
  if(sz==0) return 0;
  wp=writer((TASK)t);
  if(!wp) return 0;
  if(write_size(wp)<2) return 0;

  DBM(1,printf("env: sz=%d\n",sz));
  rmem=reader_mem(rp);
  {
    int i;
    int r=0;
    for(i=0;i<sz;i++)
    {
      if(rmem[i]>r) r=rmem[i];
      if(-rmem[i]>r) r=-rmem[i];
    }
    ((short*)writer_mem(wp))[0]=(short)r;
    produce(wp,2);
    consume(rp,sz*2);
  }
  return count;
}
SIMPLE_TASK(env)

/* root mean square */
unsigned int
task_rms_send(struct task*t)
{
  unsigned int count=0;
  struct pipe*rp,*wp;
  short*rmem;
  int sz;
  assert(xmem(t));

  rp=reader((TASK)t);
  if(!rp) return 0;
  sz=read_size(rp)/2;
  if(sz==0) return 0;
  wp=writer((TASK)t);
  if(!wp) return 0;
  if(write_size(wp)<2) return 0;

  DBM(1,printf("rms: sz=%d\n",sz));
  rmem=reader_mem(rp);
  {
    int i;
    float r=0;
    /* WARNING: for large sz we may lose precision */
    for(i=0;i<sz;i++)
      r+=(float)rmem[i]*(float)rmem[i];
    r/=(float)sz;
    r=sqrt(r);
    ((short*)writer_mem(wp))[0]=(short)r;
    produce(wp,2);
    consume(rp,sz*2);
  }
  return count;
}
SIMPLE_TASK(rms)

/*
 ***********************************************************
 */

char*
strcln(char*s)
{
  char*_s=xmalloc(strlen(s)+1);
  strcpy(_s,s);
  return _s;
}


struct task_msg_wrap
{
  struct task t;
  char* fmt;
  char msg[MSG_LEN];
  int ready;
};

unsigned int
task_msg_wrap_send(struct task_msg_wrap*t)
{
  unsigned int count=0;

  struct pipe*rp,*wp;
  rp=reader((TASK)t);
  wp=writer((TASK)t);
  if(!rp||!wp) return 0;
  if(!t->ready)
    t->ready=write_msg(wp,t->msg);
  for(; t->ready; count+=t->ready)
  { 
    char msg[MSG_LEN];
    if(!read_msg(rp,msg,MSG_LEN))
      break;
    snprintf(t->msg,MSG_LEN,t->fmt,msg);
    t->ready=write_msg(wp,t->msg);
  }
  return count;
}

void
task_msg_wrap_free(struct task_msg_wrap*t)
{
  xfree(t->fmt);
}

struct task*
task_msg_wrap_new(char* fmt)
{
  struct task_msg_wrap*t;
  t=(struct task_msg_wrap*)xcalloc(sizeof(struct task_msg_wrap));
  task_init((TASK)t,NULL,(SEND)task_msg_wrap_send,(FREE)task_msg_wrap_free);
  t->fmt=strcln(fmt);
  t->ready=1;
  return (TASK)t;
}

/*
 ***********************************************************
 */


#include "midi.h"

float
ntof(unsigned char a) /* note to freq */
{
  assert(a<128);
  return midi_freq[a];
}

static float max_log = 4.85203; /* log(128); */

float
vtor(unsigned char a) /* vel to r */
{
  assert(a<128);
  return log((float)a+1.0)/max_log;
}

int
ftos(float f) /* freq to samples at 44100 Khz mono */
{
  return (int)(44100.0/f);
}

int
ntos(unsigned char a) /* */
{
  return ftos(ntof(a));
}

/* #define DEBUG_LEVEL 1 */

struct task_midi
{
  struct task t;
  char *on_fmt, *off_fmt, *clock_fmt;
};

unsigned int
task_midi_rd_send(struct task_midi*t)
{
  unsigned int count=0;
  struct pipe*rp,*wp;
  unsigned char*rmem;
  int sz;
  assert(xmem(t));

  rp=reader((TASK)t);
  if(!rp) return 0;

  wp=writer((TASK)t);
  if(!wp) return 0;
  if(write_size(wp)==0) return 0;

  for(sz=read_size(rp);sz&&write_size(wp);sz=read_size(rp))
  {
    
    char msg[64];
    DBM(1,printf("midi_rd: sz=%d\n",sz));
    rmem=reader_mem(rp);
#define M_NOTE_ON 8
#define M_NOTE_OFF 9
#define M_CLOCK 0xF8
    if(rmem[0]>>4==8)
    {
      float f,r;
      /* note off */
      if(sz<3)
      {
        sz=reader_request(rp,3);
        if(sz<3) {printf("&&&&&&&&"); return 0;}
        rmem=reader_mem(rp);
      }
      f=ntof( rmem[1] );
      r=vtor( rmem[2] );
      snprintf(msg,64,t->off_fmt,f,r);
      consume(rp,3);
      count+=3;
    }
    else
    if(rmem[0]>>4==9)
    {
      float f,r;
      /* note on */
      if(sz<3)
      {
        sz=reader_request(rp,3);
        if(sz<3) {printf("&&&&&&&&"); return 0;}
        rmem=reader_mem(rp);
      }
      f=ntof( rmem[1] );
      r=vtor( rmem[2] );
      snprintf(msg,64,t->on_fmt,f,r);
      consume(rp,3);
      count+=3;
    }
    else
    if(rmem[0]==M_CLOCK)
    {
      consume(rp,1);
      count++;
      snprintf(msg,64,t->clock_fmt);
    }
    else
    {
      printf("midi_rd: lost a midi message: %xd\n",(int)rmem[0]);
      consume(rp,1);
      count++;
      continue;
    }
    /* send message ! */
    if(write_msg(wp,msg))
    {
      /* ok */
    }
    else
      DBM(1,printf("midi_rd: write_msg()=0\n"));
  }
  return count;
}

void
task_midi_free(struct task_midi*t)
{
  xfree(t->on_fmt);
  xfree(t->off_fmt);
  xfree(t->clock_fmt);
}

struct task*
task_midi_rd_new(char* on_fmt, char* off_fmt, char* clock_fmt)
{
  struct task_midi*t;
  t=(struct task_midi*)xcalloc(sizeof(struct task_midi));
  task_init((TASK)t,NULL,(SEND)task_midi_rd_send,(FREE)task_midi_free);
  if(on_fmt) 	t->on_fmt=strcln(on_fmt);
  else 		t->on_fmt=strcln("midi_note_on %f %f");
  if(off_fmt) 	t->off_fmt=strcln(off_fmt);
  else 		t->off_fmt=strcln("midi_note_off %f %f");
  if(clock_fmt) t->clock_fmt=strcln(clock_fmt);
  else 		t->clock_fmt=strcln("midi_clock");
  return (TASK)t;
}


/*
 ***********************************************************
 */

/* #define DEBUG_LEVEL 0 */

struct task_linear
{
  struct task t;
  int x_init;
  int x0;
  int dx; 
  int di;
  int i;
  
  int*v; /* [(di,x),...] */
  unsigned int an; /* v=malloc(an*2*sizeof(int)); */
  unsigned int n; /* n <= an */
  unsigned int idx; /* 0,...,n-1 */
};

int
task_linear_inv(struct task_linear*t)
{
  if(t->n>t->an)return 0;
  if(t->idx>=t->n && t->n)return 0;
  return 1;
}

unsigned int
task_linear_send0(struct task_linear*t)
{
  unsigned int count=0;
  struct pipe*p;
  assert(xmem(t));
  DBM(1,printf("task_linear_send x0=%d, i=%d\n, idx=%d",t->x0,t->i,t->idx));
  assert(t->n);
  if(t->n==0)return 0;
  assert(task_linear_inv(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p)/2;
    if(size)
    {
      int j;
      short*mem=writer_mem(p);
      /* int di; */
      assert(t->idx<t->n);
      /* di=t->v[t->idx*2];  */
      for(j=0;j<size;j++)
      {
        mem[j]=t->i*t->dx/t->di+t->x0; /* XXX the multiply overflows */

#if 0
        int temp1,temp2,temp3;
        temp1=t->i*t->dx/t->di+t->x0; /* optimize me */
        temp2=t->i*t->dx;
        temp3=(t->i*t->dx)/t->di;
        mem[j]=temp1;
        if(t->i%128==0)
        printf( "x0=%d dx=%d di=%d i=%d, idx=%d, %d %d %d\n", 
          t->x0, t->dx, t->di, t->i, t->idx, temp1, temp2, temp3 ); 
#endif

        t->i++;
        if(t->i>t->di)
        {
          int x;
          /* x=t->v[t->idx*2+1];  */
          /* if(mem[j]!=x) */
            /* {printf(" * linear error =%d\n",mem[j]-x );} */
          t->i=1;
          t->idx=(t->idx+1)%t->n;
          t->x0=mem[j];
          t->di=t->v[t->idx*2]; assert(t->di);
          x=t->v[t->idx*2+1]; 
          t->dx=x-t->x0;
        }
      }
      produce(p,size*2);
      count+=size*2;
    }
  }
  /* printf( "\n" ); */
  assert(task_linear_inv(t));
  return count;
}

unsigned int
task_linear_send1(struct task_linear*t)
{
  unsigned int count=0;
  struct pipe*p;
  assert(xmem(t));
  DBM(1,printf("task_linear_send x0=%d, i=%d\n, idx=%d",t->x0,t->i,t->idx));
  assert(t->n);
  if(t->n==0)return 0;
  assert(task_linear_inv(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p)/2;
    if(size)
    {
      int j;
      short*mem=writer_mem(p);
      /* int di; */
      assert(t->idx<t->n);
      /* di=t->v[t->idx*2];  */
      for(j=0;j<size;j++)
      {
        float m;
        m = t->dx / (float)t->di;
        mem[j] = (int)(t->i*m) + t->x0;  
        /* mem[j] = lrint(t->i*m) + t->x0;  */
        t->i++;
        if(t->i>t->di)
        {
          int x;
          /* x=t->v[t->idx*2+1];  */
          /* if(mem[j]!=x) */
            /* {printf(" * linear error =%d\n",mem[j]-x );} */
          t->i=1;
          t->idx=(t->idx+1)%t->n;
          t->x0=mem[j];
          t->di=t->v[t->idx*2]; assert(t->di);
          x=t->v[t->idx*2+1]; 
          t->dx=x-t->x0;
        }
      }
      produce(p,size*2);
      count+=size*2;
    }
  }
  /* printf( "\n" ); */
  assert(task_linear_inv(t));
  return count;
}

void
task_linear_probe(struct task_linear*t)
{
  /* what send should we use ? */
  int idx;
  int x;
  assert(xmem(t));
  assert(task_linear_inv(t));
  x = t->x_init;
  for (idx=0;idx<t->n;idx++)
  {
    int di, _x, dx;
    di = t->v[idx*2];
    _x = t->v[idx*2+1];
    dx = x-_x;
    /* printf("  **  task_linear_probe %p: x=%d _x=%d di=%d dx=%d\n", t, x, _x, di, dx ); */
    if ( (di*dx)/di != dx )
    {
      /* int overflow would occur */
      DBM(1,printf("  **  task_linear_probe %p: using overflow safe.\n", t ));
      t->t.send = (SEND)task_linear_send1;
      return;
    }
    x = _x;
  }
  t->t.send = (SEND)task_linear_send0; /* no overflow */
  DBM(1,printf("  **  task_linear_probe %p: no overflow detected.\n", t ));
}

void
task_linear_free(struct task_linear*t)
{
  assert(xmem(t));
  assert(task_linear_inv(t));
  xfree(t->v);
  t->v = NULL;
}

void
task_linear_reset(struct task_linear*t)
{
  assert(xmem(t));
  t->idx=0;
  if(t->n)
  {
    t->i=1;
    t->x0=t->x_init;
    t->di=t->v[0];
    t->dx=t->v[1];
  }
  assert(task_linear_inv(t));
}

struct task*
task_linear_new(int n, short x_init)
{
  struct task_linear*t;
  t=(struct task_linear*)xcalloc(sizeof(struct task_linear));
  task_init((TASK)t,
    (RESET)task_linear_reset,
    (SEND)task_linear_send0,
    (FREE)task_linear_free);
  t->an=n;
  t->n=0;
  t->v=(int*)xmalloc(sizeof(int)*2*t->an);

  t->x_init=x_init;   /* XXX why remember this ? */
  t->x0=x_init;
  t->dx=0; 
  t->i=1;
  t->di=1;
  task_linear_probe(t);
  assert(task_linear_inv(t));
  return (TASK)t;
}

void
task_linear_setitem(struct task*_t, unsigned int idx, int di, int x)
{
  struct task_linear*t;
  t=(struct task_linear*)_t;
  assert(xmem(t));
  assert(task_linear_inv(t));
  assert(idx<t->n);
  assert(di>0);
  t->v[idx*2]=di;
  t->v[idx*2+1]=x;
  task_linear_probe(t);
}

void
task_linear_append(struct task*_t, int di, int x)
{
  struct task_linear*t;
  t=(struct task_linear*)_t;
  assert(xmem(t));
  assert(task_linear_inv(t));
  if(t->n==t->an)
  {
    /* grow */
    t->an<<=1;
    t->v=(int*)xrealloc(t->v,sizeof(int)*2*t->an);
  }
  t->n++;
  task_linear_setitem(_t,t->n-1,di,x);
  if(t->n==1)
    { t->di=di; t->dx=x-t->x0; }
  task_linear_probe(t);
  assert(task_linear_inv(t));
}

void
task_linear_pop(struct task*_t)
{
  struct task_linear*t;
  t=(struct task_linear*)_t;
  assert(xmem(t));
  assert(task_linear_inv(t));
  assert(t->n);
  t->n--;
  task_linear_probe(t);
  assert(task_linear_inv(t));
}

