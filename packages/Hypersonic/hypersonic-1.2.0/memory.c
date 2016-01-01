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
#include <assert.h>
#include "memory.h"
#include "debug.h"

int _malloced=0;
int mark;

#define MEM_MAGIC 0xFEF5
#define MEM_FREED 0xDDE1

#define DEBUG_LEVEL 0

#ifdef MEMORY_CHECK
void*
xmalloc(size_t s)
{
  int*p=(int*)malloc(s+2*sizeof(int));
  ENTER();
  if (p==NULL)
  {
    fprintf(stderr,"malloc bomb.\n");
    assert(0);
    exit(EXIT_FAILURE);
  }
  p[0]=MEM_MAGIC;
  assert(p[0]==MEM_MAGIC);
  p[1]=s;
  _malloced+=s;
  DBM(1,printf("malloc(%d)=%p, total=%d\n",s,p,_malloced));
  LEAVE();
  return (void*)(p+2);
}

void*
xcalloc(size_t s)
{
  int*p=(int*)calloc(1,s+2*sizeof(int));
  ENTER();
  if(p==NULL)
  {
    fprintf(stderr,"malloc bomb.\n");
    assert(0);
    exit(EXIT_FAILURE);
  }
  p[0]=MEM_MAGIC;
  assert(p[0]==MEM_MAGIC);
  p[1]=s;
  _malloced+=s;
  DBM(1,printf("calloc(%d)=%p, total=%d\n",s,p,_malloced));
  /*DBM(1,printf("xcalloc(%p) p[0]=%d, p[1]=%d\n",p,p[0],p[1]));*/
  p=p+2;
  LEAVE();
  return p;
}

void*
xrealloc(void*p,size_t s)
{
  if(p==NULL)
    return xmalloc(s);
  ENTER();
  p=((int*)p)-2;
  assert(((int*)p)[0]==MEM_MAGIC);
  _malloced-=((int*)p)[1];
  p=realloc(p,s+2*sizeof(int));
  if (p==NULL)
  {
    fprintf(stderr,"realloc bomb.\n");
    assert(0);
    exit(EXIT_FAILURE);
  }
  ((int*)p)[1]=s;
  _malloced+=s;
  DBM(1,printf("realloc(?,%d)=%p, total=%d\n",s,p,_malloced));
  p=((int*)p)+2;
  LEAVE();
  return p;
}

int
xmem(void*p)
{
  int *_p=(int*)p;
  /*printf("xmem(%p)\n",p);*/
  /* mem check */
  if(p==NULL)
  { printf("xmem(NULL)\n"); return 0; }
  _p-=2;
  if (_p[0]==MEM_FREED)
  { printf("xmem(%p) freed!\n",p); return 0; }
  if (_p[0]!=MEM_MAGIC)
  {
    printf("xmem(%p) *[0]=%d, *[1]=%d: no magic\n",_p,_p[0],_p[1]);
    return 0;
  }
  return 1;
}

void
xmark()
{
  ENTER();
  mark=_malloced;
  DBM(1,printf(" memory.c xmark() : %d malloced\n", _malloced ));
  LEAVE();
}

int
xcheck()
{
  ENTER();
  DBM(1,printf(" memory.c xcheck() : %d malloced\n", _malloced ));
  LEAVE();
  return _malloced-mark;
}

void
xfree(void*p)
{
  ENTER();
  p=((int*)p)-2;
  DBM(1,printf("free(%p)",p));
  if(((int*)p)[0]!=MEM_MAGIC)
  {
    fprintf(stderr,"xfree bomb.\n");
    if(((int*)p)[0]==MEM_FREED)
      fprintf(stderr,"mem freed!\n");
    assert(0);
    exit(EXIT_FAILURE);
  }
  _malloced-=((int*)p)[1];
  ((int*)p)[0]=MEM_FREED;
  DBM(1,printf(" -%d, total=%d\n",((int*)p)[1],_malloced));
  free(p);
  LEAVE();
}

#endif
