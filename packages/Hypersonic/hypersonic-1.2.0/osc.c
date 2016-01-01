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

#include <sys/stat.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <assert.h>
#include <math.h>
#include "memory.h"
#include "task.h"

extern int srate;
#define SRATE srate

struct task_tri
{
  struct task t;
  float x,dx;
  float sgn;
  float r; /* amplitude */
  float f;
};

unsigned int
task_tri_send(struct task_tri*t);

void
task_tri_set_f(struct task*_t,float f)
{
  struct task_tri*t=(struct task_tri*)_t;
  assert(xmem(t));
  t->f=f;
  t->dx=4.0*t->f*t->r/SRATE;
}

void
task_tri_set_r(struct task*_t,float r)
{
  struct task_tri*t=(struct task_tri*)_t;
  assert(xmem(t));
  t->r=r;
  t->dx=4.0*t->f*r/SRATE;
}

struct task*
task_tri_new(float f,float r)
{
  MAKE(struct task_tri,t);
  //printf("task_tri_new f=%f, r=%f\n", f, r );
  task_init((TASK)t,NULL,(SEND)task_tri_send,NULL);
  t->x=0.0;
  t->dx=4.0*f*r/SRATE;
  t->r=r;
  t->f=f;
  t->sgn=1.0;
  return (TASK)t;
}

unsigned int
task_tri_send(struct task_tri*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  //printf("task_tri_send dx=%f\n", t->dx );
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p);
    if(size)
    {
      int j;
      short*mem=writer_mem(p);
#if 0
      struct pipe*fp=NULL,*ap=NULL;
      fp=reader((TASK)t);
      if(fp)
        ap=next_reader((TASK)t,fp);
#endif
      for(j=0;j<size/2;j++)
      {
        mem[j]=(1<<14)*t->x;
        if(t->x>t->r) {t->sgn=-1.0;}
        if(t->x<-t->r) {t->sgn=+1.0;}
        t->x+=t->sgn*t->dx;
      }
      produce(p,size);
      i+=size;
    }
  }
  return i;
}

/*
 *******************************************************
 */

struct task_squ
{
  struct task t;
  int n, i;
  float r; /* amplitude */
};

unsigned int
task_squ_send(struct task_squ*t);

void
task_squ_set_f(struct task*_t,float f)
{
  struct task_squ*t=(struct task_squ*)_t;
  assert(xmem(t));
  t->n=(int)floor(SRATE/(2*f));
  t->i=t->n;
}

void
task_squ_set_r(struct task*_t,float r)
{
  struct task_squ*t=(struct task_squ*)_t;
  assert(xmem(t));
  if(t->r<0)
    t->r=-r;
  else
    t->r=r;
}

struct task*
task_squ_new(float f,float r)
{
  MAKE(struct task_squ,t);
  task_init((TASK)t,NULL,(SEND)task_squ_send,NULL);
  task_squ_set_f((TASK)t,f);
  t->i=t->n;
  t->r=r;
  return (TASK)t;
}

/* [float freq,[float amp]]->short */
unsigned int
task_squ_send(struct task_squ*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p);
    if(size)
    {
      int j;
      short*mem=writer_mem(p);
      struct pipe*fp=NULL,*ap=NULL;
      fp=reader((TASK)t);
      if(fp)
        ap=next_reader((TASK)t,fp);
      for(j=0;j<size/2;j++)
      {
        mem[j]=(1<<14)*t->r;
        if(!t->i--) { t->r=-t->r; t->i=t->n; }
      }
      produce(p,size);
      i+=size;
    }
  }
  return i;
}

/*
 *******************************************************
 */

struct task_sin
{
  struct task t;
  float x,y,mx,my;

  float r; /* amplitude */
  float _r; /* target amplitude */
  int dr; /* r is changing to _r */
};

unsigned int
task_sin_send(struct task_sin*t);

void
task_sin_set_f(struct task*_t,float f)
{
  struct task_sin*t=(struct task_sin*)_t;
  assert(xmem(t));
  t->mx=cos(2*M_PI*f/SRATE);
  t->my=-sin(2*M_PI*f/SRATE); /* why minus ? */
}

void
task_sin_set_p(struct task*_t,float p)
{
  struct task_sin*t=(struct task_sin*)_t;
  assert(xmem(t));
  t->x=t->r*cos(p);
  t->y=t->r*sin(-p); /* why minus ? */
}

static void
__sin_set_r(struct task_sin*t,float r)
{
  float norm;
  assert(xmem(t));
  t->r=r;
  norm=sqrt(t->x*t->x+t->y*t->y);
#if ASSERT_NORM
  assert(norm>0.00001);
#else
  if(norm<0.00001)
  {t->x=0.0;t->y=r;return;}
#endif
  r/=norm;
  t->x*=r;
  t->y*=r;
}

static float dr=0.001;
static void
__sin_update_r(struct task_sin*t)
{
  assert(xmem(t));
  if(t->dr>0) 
  { __sin_set_r(t,t->r+dr);
    if(t->r>=t->_r) t->dr=0; /* stop */}
  else
  if(t->dr<0)
  { __sin_set_r(t,t->r-dr);
    if(t->r<=t->_r) t->dr=0; /* stop */}
}

void
task_sin_set_r(struct task*_t,float r)
{
  struct task_sin*t=(struct task_sin*)_t;
  assert(xmem(t));
  if(t->r<r) t->dr=1;
  else
  if(t->r>r) t->dr=-1;
  t->_r=r;
}

struct task*
task_sin_new(float f,float r)
{
  struct task_sin*t;
  //printf("task_sin_new f=%f, r=%f\n", f, r );
  t=(struct task_sin*)xcalloc(sizeof(struct task_sin));
  task_init((TASK)t,NULL,(SEND)task_sin_send,NULL);
  t->r=r;
  t->_r=r;
  t->dr=0;
  t->x=r;
  t->y=0.0;
  task_sin_set_f((TASK)t,f);
  return (TASK)t;
}

/* [float freq,[float amp]]->short */
unsigned int
task_sin_send(struct task_sin*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p);
    if(size)
    {
      int j;
      short*mem=writer_mem(p);
      struct pipe*fp=NULL,*ap=NULL;
      fp=reader((TASK)t);
      if(fp)
        ap=next_reader((TASK)t,fp);
      for(j=0;j<size/2;j++)
      {
        float x;
        mem[j]=(1<<14)*t->y;
        x = t->mx*t->x - t->my*t->y;
        t->y = t->y*t->mx + t->x*t->my;
        t->x=x;
        if(t->dr) __sin_update_r(t);
      }
/*
      float r;
      r=sqrt(t->x*t->x+t->y*t->y);
      t->x*=t->r/r;
      t->y*=t->r/r;
*/
      produce(p,size);
      i+=size;
    }
  }
  return i;
}

/*
 *******************************************************
 */

static unsigned long u = 1;

unsigned int
task_noise_send(struct task*t)
{
  unsigned int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p)/4;
    if(size)
    {
      unsigned long*mem=writer_mem(p);
      for(;i<size;i++)
      {
        mem[i]=u;
        u=u*1103515245+12345;
      }
      produce(p,i*4);
    }
    else
    {
      writer_request(p,4);
    }
  }
  return i;
}
SIMPLE_TASK(noise)


/*
 ***********************************************************
 */

#if 0 /* terrible buzzing sounds */

/* van der pol equation */
struct task_vdp
{
  struct task t;
  float e;
  float x;
  float dx;
  float ddx;
};

unsigned int
task_vdp_send(struct task_vdp*t)
{
  unsigned int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p)/2;
    if(size)
    {
      char*mem=writer_mem(p);
      for(;i<size;i++)
      {
        float _dx;
        mem[i]=(short)(t->x);
        _dx = (t->ddx+t->x) / (t->e*(1.0-t->x*t->x));
        t->ddx = _dx - t->dx;
        t->dx = _dx;
        t->x += t->dx;
      }
      produce(p,i*2);
    }
    else { writer_request(p,2); }
  }
  return i*2;
}

void
task_vdp_free(struct task_vdp*t)
{
  assert(xmem(t));
}

struct task*
task_vdp_new(float e)
{
  struct task_vdp*t;
  t=(struct task_vdp*)xcalloc(sizeof(struct task_vdp));
  task_init((TASK)t,NULL,(SEND)task_vdp_send,(FREE)task_vdp_free);
  t->e=e;
  t->x=0.1;
  t->dx=0.0;
  t->ddx=0.0;
  return (TASK)t;
}


/*
 ***********************************************************
 */

struct task_chaos
{
  struct task t;
  float x, y;
  float cx, cy;
};

unsigned int
task_chaos_send(struct task_chaos*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p)/2;
    if(size)
    {
      char*mem=writer_mem(p);
      for(;i<size;i++)
      {
        float _x;
        mem[i]=(short)((1<<14)*(t->x));
        _x = t->x*t->x - t->y*t->y;
        t->y = 2*t->x*t->y;
        t->x = _x;
        t->x += t->cx;
        t->y += t->cy;
      }
      produce(p,i*2);
    }
    else { writer_request(p,2); }
  }

  return i;
}

void
task_chaos_set_c(struct task*_t,float cx, float cy)
{
  struct task_chaos*t=(struct task_chaos*)_t;
  assert(xmem(t));
  t->cx=cx;
  t->cy=cy;
}

void
task_chaos_free(struct task_chaos*t)
{
  assert(xmem(t));
}

struct task*
task_chaos_new(float cx, float cy)
{
  struct task_chaos*t;
  t=(struct task_chaos*)xcalloc(sizeof(struct task_chaos));
  task_init((TASK)t,NULL,(SEND)task_chaos_send,(FREE)task_chaos_free);
  t->cx=cx;
  t->cy=cy;
  t->x=0.0;
  t->y=0.0;
  return (TASK)t;
}


#endif



/*
 ***********************************************************
 */

struct task_poly
{
  struct task t;

  float *v; /* derivatives: x, dx, ddx, etc */
  int nv; /* order+1: len(v) */
  float r; /* gain */

  float alpha;
  float *u; /* DC components (mean/average) */
  int nu; /* len(u) */
};

unsigned int
task_poly_send(struct task_poly*t)
{
  int i=0;
  struct pipe*p;
  assert(xmem(t));
  p=writer((TASK)t);
  if(p)
  {
    int size=write_size(p)/2;
    if(size)
    {
      short*mem=writer_mem(p);
      for(i=0;i<size;i++)
      {
        int j;
        mem[i]=(short)(t->v[0]*t->r);
        for(j=t->nv-1;j;j--)
        {
          /* printf( "%.2f ", t->v[j] );  */
          t->v[j-1] += t->v[j];
        }
        for(j=0;j<t->nu;j++)
        {
          t->u[j] = t->alpha*t->v[j] + (1.0-t->alpha)*t->u[j]; 
          t->v[j] -= t->u[j]; /* subtract DC */
        }
        /* printf( "%.2f\n", t->v[0] );  */
      }
      produce(p,i*2);
    }
    /* else { writer_request(p,2); } */
  }
  return i*2;
}

void
task_poly_free(struct task_poly*t)
{
  assert(xmem(t));
  xfree(t->v);
  t->v = NULL;
  xfree(t->u);
  t->u = NULL;
}

/*
 * task_poly_new(int nv, float r, int nu, float alpha )
 *   nv - number of derivatives (from 0th derivative)
 *   r  - gain
 *   nu - number of dc components to compute and subtract
 *   alpha - used to compute d.c. (1.0>=alpha>=0)
 *     1.0 subtract all
 *     0.0 subtract none
 */
struct task*
task_poly_new(int nv, float r, int nu, float alpha )
{
  struct task_poly*t;
  t=(struct task_poly*)xcalloc(sizeof(struct task_poly));
  task_init((TASK)t,NULL,(SEND)task_poly_send,(FREE)task_poly_free);
  assert(nu>0);
  t->nv=nv;
  t->nu=nu;
  t->r=r;
  t->alpha = alpha;
  assert( nu < nv );
  assert( nu >= 0 );
  t->v=(float*)xcalloc(sizeof(float)*t->nv);
  if (nu)
    t->u=(float*)xcalloc(sizeof(float)*t->nu);
  else
    t->u=NULL;
  return (TASK)t;
}

void
task_poly_set_r(struct task*_t, float r)
{
  struct task_poly*t=(struct task_poly*)_t;
  assert(xmem(t));
  t->r=r;
}

void
task_poly_set_alpha(struct task*_t, float alpha)
{
  struct task_poly*t=(struct task_poly*)_t;
  assert(xmem(t));
  t->alpha=alpha;
}

void
task_poly_set_v(struct task*_t, int i,float x)
{
  struct task_poly*t=(struct task_poly*)_t;
  assert(xmem(t));
  assert(0<=i);
  assert(i<t->nv);
  /* printf( "set v %d %.2f\n", i, x ); */
  t->v[i]=x;
}

float
task_poly_get_v(struct task*_t, int i)
{
  struct task_poly*t=(struct task_poly*)_t;
  assert(xmem(t));
  assert(0<=i);
  assert(i<t->nv);
  return t->v[i];
}

