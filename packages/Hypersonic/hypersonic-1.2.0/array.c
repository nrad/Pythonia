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
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <assert.h>
#include "array.h"
#include "memory.h"
#include "debug.h"

/* #define DEBUG_LEVEL 1 */

struct array*
array_alloc()
{
  struct array*a;
  a=(struct array*)xcalloc(sizeof(struct array));
  return a;
}

struct array*
array_new(int sz)
{
  struct array*a;
  a=array_alloc();
  a->mem=xmalloc(sz);
  a->sz=sz;
  a->a=NULL;
  a->refc=0;
  a->free=NULL;
  return a;
}

void
array_free_mmap(struct array*a);

struct array*
array_new_mmap(char*filename)
{
  struct array*a;
  struct stat sbuf;
  int fd;
  fd=open(filename,O_RDONLY);
  if(fd<0) 
  {
    printf("*** array_new_mmap error ***\n");
    assert(0);
    return NULL;
  }
  a=array_alloc();
  fstat(fd,&sbuf);
  a->sz=sbuf.st_size;
  a->mem=mmap(NULL,a->sz,PROT_READ,MAP_PRIVATE,fd,0);
  close(fd);
  /* printf("array_new_mmap: file '%s' fd %d size %d, at %p\n", */
    /* filename, fd, a->sz, a->mem ); */
  a->a=NULL;
  a->refc=0;
  a->free=array_free_mmap;
#if 0
  {
    int i,j;
    for(i=0;i<a->sz;i++)
      j=((char*)a->mem)[i];
  }
#endif
  return a;
}

void
array_set_short(struct array*a, int i, short x)
{
  assert(xmem(a));
  assert(i>=0);
  assert(i<a->sz/2);
  ((short*)(a->mem))[i]=x;
}

short
array_get_short(struct array*a, int i)
{
  assert(xmem(a));
  assert(i>=0);
  assert(i<a->sz/2);
  return ((short*)(a->mem))[i];
}

void
array_free_sub(struct array*a);

struct array*
array_new_sub(struct array*a,int _i,int i)
{
  struct array*_a;
  assert(xmem(a));
  _a=array_alloc();
  assert(i>_i);
  assert(i<=a->sz-_i);
  _a->sz=i-_i;
  _a->mem=((char*)a->mem)+_i;
  a->refc++;
  _a->refc=0;
  _a->a=a;
  _a->free=NULL;
  return _a;
}

void*
array_mem(struct array*a)
{
  assert(xmem(a));
  /* printf("array_mem %p\n",a->mem); */
  return a->mem;
}

int
array_sz(struct array*a)
{
  assert(xmem(a));
  return a->sz;
}

/* struct task* */
/* task_array_rd_new(struct array*a) */

void
array_free_mmap(struct array*a)
{
  munmap(a->mem,a->sz);
}

void
array_free_sub(struct array*a)
{
}

void
array_free(struct array*a)
{
  assert(xmem(a));
  assert(a->refc==0);
  if(a->a)
  {
    a->a->refc--;
    assert(a->a->refc>=0);
  }
  if(a->free)
    (*a->free)(a);
  else
  if(a->a==NULL)
    xfree(a->mem);
  xfree(a);
}



