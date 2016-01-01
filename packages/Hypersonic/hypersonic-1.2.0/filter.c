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
#include "debug.h"

struct task_fir
{
  struct task t;
  float*fir;
  int len;
};

unsigned int
task_fir_send(struct task_fir*t);

static float*
fclone(float*fir, int len)
{
  float*_fir=xmalloc(len*sizeof(float));
  memcpy(_fir,fir,len*sizeof(float));
  return _fir;
}

void
task_fir_free(struct task_fir*t)
{
  xfree(t->fir);
}

struct task*
task_fir_new(float*fir/* gets cloned */, int len )
{
  struct task_fir*t;
  t=(struct task_fir*)xcalloc(sizeof(struct task_fir));
  task_init((TASK)t,NULL,(SEND)task_fir_send,(FREE)task_fir_free);
  t->fir=fclone(fir,len);
  t->len=len;
  return (TASK)t;
}

struct task*
task_fdelta_new(float w)
{
  float fir[2];
  fir[0]=-1.0/w; fir[1]=+1.0/w;
  return task_fir_new(fir,2);
}

/* short->short */
unsigned int
task_fir_send(struct task_fir*t)
{
  int count=0;
  struct pipe*wp,*rp;
  assert(xmem(t));
  rp=reader((TASK)t);
  wp=writer((TASK)t);
  if(!rp||!wp)
    return 0;
  reader_request(rp,t->len*2);
  if(write_size(wp)>=2 && read_size(rp)>=t->len*2)
  {
#if 1
    while(write_size(wp)>=2 && read_size(rp)>=t->len*2)
    {
      short*wmem=(short*)writer_mem(wp);
      short*rmem=(short*)reader_mem(rp);
      int j;
      float x=0.0;
      for(j=0;j<t->len;j++)
        x+=t->fir[t->len-j-1]*rmem[j];
      *wmem=x;
      produce(wp,2);
      consume(rp,2);
      count+=2;
    }
#else /* why doesn't this work? */
    short*wmem=(short*)writer_mem(wp);
    short*rmem=(short*)reader_mem(rp);
    int i,size;
    size=MIN(write_size(wp),read_size(rp)-t->len*2);
    size/=2;
    printf("read_size=%d\n",read_size(rp));
    for(i=0;i<size;i++)
    {
      int j;
      float x=0.0;
      for(j=0;j<t->len;j++)
        x+=t->fir[t->len-j-1]*rmem[j+i];
      wmem[i]=x;
    }
    i*=2;
    produce(wp,i);
    consume(rp,i);
    count+=i;
#endif
  }
  else if(0)
  {
    printf("nope\n");
  }
  return count;
}

/*
 ***********************************************************
 */

/* sparse IIR 
 */

struct task_iir;
struct tap
{
  struct link k;
  int i; /* whence */
  int x;
  struct task_iir*t;
};

struct tap*
tap_new(struct task_iir*t,int i, int x)
{
  struct tap*tp=xcalloc(sizeof(struct tap));
  tp->i=i;
  tp->x=x;
  tp->t=t;
  return tp;
}

void
task_iir_bound(struct task_iir*t,int i);
void
tap_set_i(struct tap*tp,int i)
{
  assert(xmem(tp));
  DBM(1,printf("tap_set_i %d\n", i));
  tp->i=i;
  task_iir_bound(tp->t,i);
}

void
tap_set_x(struct tap*tp,int x)
{
  assert(xmem(tp));
  DBM(1,printf("tap_set_x %d\n", x));
  tp->x=x;
}

void
tap_free(struct tap*tp)
{
  assert(xmem(tp));
  xfree(tp);
}
  
/*****************/

struct task_iir
{
  struct task t;
  struct list line;
  int pos; /* extent */
  int neg; /* extent */
  int i; /* filled to writer_mem(wp)[i] */
};

unsigned int
task_iir_send(struct task_iir*t)
{
  unsigned int count=0;
  struct pipe*wp,*rp;
  int i;
  assert(xmem(t));
  rp=reader((TASK)t); wp=writer((TASK)t);
  if(!rp||!wp) return 0;
  i=t->i; /* recall i */
  reader_request(rp,2*(t->pos+1)); writer_request(wp,2*(i+1));
  /* printf("task_iir_send %s i=%d\n", task_str((TASK)t), i); */
  while(2*i<write_size(wp) && 2*t->pos<read_size(rp))
  {
    short*wmem=(short*)writer_mem(wp);
    short*rmem=(short*)reader_mem(rp);
    struct tap*tp;
    /* int j; */
    int x=0;
    assert(2*i<=write_size(wp));
    /* printf("  task_iir_send %s i=%d\n", task_str((TASK)t), i);  */
    for(tp=list_first(&t->line);tp;tp=list_next(&t->line,tp))
    {
      /* printf("    task_iir_send tp->i=%d \n", tp->i );  */
      assert(xmem(tp)); 
      if(tp->i>=0) 
      {
        assert(2*tp->i<read_size(rp));
        /* printf("    task_iir_send rmem=%d\n", rmem[tp->i]); */
        x+=(short)( ((int)rmem[tp->i]*(int)tp->x)>>15 );
      }
      else 
      {
        assert(2*(i+tp->i)<(int)write_size(wp));
        if(0<i+tp->i)
          {x+=(short)(((int)wmem[i+tp->i]*(int)tp->x)>>15);}
        /* else x+=0; */
      }
    }
    /* for(j=0;j<t->len;j++) */
      /* x+=t->fir[t->len-j-1]*rmem[j]; */

    wmem[i++]=x;
    while(0<i+t->neg-1) { produce(wp,2); i-=1; }
    consume(rp,2);
    count+=2;
  }
  /* printf("task_iir_send %s i=%d\n", task_str((TASK)t), i);  */
  t->i=i; /* remember i */
  return count;
}

void
task_iir_remove(struct task*_t,struct tap*tp);

void
task_iir_free(struct task_iir*t)
{
  struct tap*tp;
  assert(xmem(t));
  while((tp=list_first(&t->line)))
    task_iir_remove((struct task*)t,tp);
}

struct task*
task_iir_new()
{
  struct task_iir*t;
  t=(struct task_iir*)xcalloc(sizeof(struct task_iir));
  task_init((TASK)t,NULL,(SEND)task_iir_send,(FREE)task_iir_free);
  list_init(&t->line);
  /* t->pos=0; */
  t->pos=1;
  t->neg=0;
  t->i=0;
  return (TASK)t;
}

void
task_iir_bound(struct task_iir*t,int i)
{
  assert(xmem(t));
  if(i>=0) t->pos=MAX(i,t->pos);
  if(i<0) t->neg=MIN(i,t->neg);
}

struct tap*
task_iir_add(struct task*_t,int i, int x)
{
  struct task_iir*t=(struct task_iir*)_t;
  struct tap*tp;
  assert(xmem(t));
  tp=tap_new(t,i,x);
  list_append(&t->line,tp); /* not stored in order */
  task_iir_bound(t,i);
  return tp;
}

void
task_iir_remove(struct task*_t,struct tap*tp)
{
  struct task_iir*t=(struct task_iir*)_t;
  /* struct tap*tp; */
  assert(xmem(t));
  list_remove(&t->line,tp);
  tap_free(tp);
  /* pos & neg don't shrink */
}

/*
 ***********************************************************
 */

struct task_resample
{
  struct task t;
  float r; /* dilation ratio */
  float i; /* leftover: where in input are we? */
};

unsigned int
task_resample_send(struct task_resample*t);

/* short */
struct task*
task_resample_new(float r)
{
  struct task_resample*t;
  assert(r>0);
  t=(struct task_resample*)xcalloc(sizeof(struct task_resample));
  task_init((TASK)t,NULL,(SEND)task_resample_send,NULL);
  assert(r>0.0);
  t->r=r;
  t->i=0.0;
  return (TASK)t;
}

void
task_resample_set_r(struct task*_t,float r)
{
  struct task_resample*t;
  assert(xmem(_t));
  t=(struct task_resample*)_t;
  assert(t->r>=0.0);
  t->r=r;
}

/* short */
/* mono -> mono */
unsigned int
task_resample_send(struct task_resample*t)
{
  unsigned int count=0,o;
  unsigned int rsize,wsize;
  struct pipe*wp,*rp;
  /* struct task*t=(TASK)t; */
  float i,r;
  short*rmem,*wmem;
  assert(xmem(t));
  rp=reader((TASK)t);
  if(!rp)return 0;
  wp=writer((TASK)t);
  if(!wp)return 0;

  i=t->i; r=t->r;
  rsize=read_size(rp);
  if(rsize<ceil(i+r)*2+2)
    rsize=reader_request(rp,2*ceil(i+r)+2);
  if(rsize<4) /* need two samples */
    rsize=reader_request(rp,4);
  /* assert( rsize <= read_size(rp) ); */ /* No! */
  rsize = read_size(rp);
  if(rsize<4)return 0;

  wsize=write_size(wp);
  if(wsize<2)
    wsize=writer_request(wp,2);
  if(wsize<2)return 0;

  DBM(1, printf("\n  resample rsize=%d,wsize=%d\n",rsize,wsize));
  /*sleep(1);*/
  rmem=reader_mem(rp);
  wmem=writer_mem(wp);
  /*printf("  resample r=%.1f, i=%.1f\n",t->r,t->i);*/
  assert(t->i>=0);
  assert(t->r>0);
  for( o=0; o<wsize/2 && i+ceil(r)<rsize/2; o++, i+=r )
  {
    /*printf( "  i=%.2f o=%d\n", i, o );*/
    /* linear interpolation */
    wmem[o] = (short)
    (
      (float)rmem[(int)floor(i)] * (1-(i-floor(i))) +
      (float)rmem[(int)floor(i)+1] * (i-floor(i))
    );
  }
  /*printf("  resample produce %d\n",o*2);*/
  produce( wp, o*2 );
  count += o*2;
  if(i>=1.0)
  {
    assert( ((int)floor(i))*2 <= read_size(rp) );
    consume(rp,((int)floor(i))*2);
    /*printf("  resample consume %d\n",(int)floor(i)*2);*/
    count += floor(i)*2;
  }
  t->i = i-floor(i);
  return count;
}

/*
 ***********************************************************
 */

struct task_lo
{
  struct task t;
  float r; /* constant */
  float x; /* wmem[i-1] */
};

unsigned int
task_lo_send(struct task_lo*t);

struct task*
task_lo_new( float r )
{
  struct task_lo*t;
  t=(struct task_lo*)xcalloc(sizeof(struct task_lo));
  task_init((TASK)t,NULL,(SEND)task_lo_send,NULL);
  t->r=r;
  t->x=0.0;
  return (TASK)t;
}

void
task_lo_set_r(struct task*t,float r)
{
  ((struct task_lo*)t)->r=r;
}

unsigned int
task_lo_send(struct task_lo*t)
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
  {
    wmem[i]=(short)( (t->x+t->r*(float)rmem[i])/(t->r+1.0) );
    t->x=(float)wmem[i];
  }
  consume(rp,size*2);
  produce(wp,size*2);
  count+=size*2;
  return count;
}


/*
 ***********************************************************
 */

struct task_hi
{
  struct task t;
  float r; /* constant */
  short x; /* wmem[i-1] */
  short y; /* rmem[i-1] */
};

unsigned int
task_hi_send(struct task_hi*t);

struct task*
task_hi_new( float r )
{
  struct task_hi*t;
  t=(struct task_hi*)xcalloc(sizeof(struct task_hi));
  task_init((TASK)t,NULL,(SEND)task_hi_send,NULL);
  t->r=r;
  t->x=0.0;
  t->y=0.0;
  return (TASK)t;
}

void
task_hi_set_r(struct task*t,float r)
{
  ((struct task_hi*)t)->r=r;
}

unsigned int
task_hi_send(struct task_hi*t)
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
  {
    wmem[i]=(short)( (rmem[i]-t->y+t->x)/(t->r+1.0) );
    t->x=wmem[i];
    t->y=rmem[i];
  }
  consume(rp,size*2);
  produce(wp,size*2);
  count+=size*2;
  return count;
}

/*
 ***********************************************************
 */

/* parallel LC circuit */
struct task_band
{
  struct task t;
  /* constants */
  float r1; /* ~= RLh */
  float r2; /* ~= RC/h */

  short x; /* wmem[i-1] */
  short y; /* (sum wmem)[i-1] */
};

unsigned int
task_band_send(struct task_band*t);

struct task*
task_band_new( float r1, float r2 )
{
  struct task_band*t;
  t=(struct task_band*)xcalloc(sizeof(struct task_band));
  task_init((TASK)t,NULL,(SEND)task_band_send,NULL);
  t->r1=r1;
  t->r2=r2;
  t->x=0.0;
  t->y=0.0;
  return (TASK)t;
}

void
task_band_set_r(struct task*t,float r1,float r2)
{
  ((struct task_band*)t)->r1=r1;
  ((struct task_band*)t)->r2=r2;
}

unsigned int
task_band_send(struct task_band*t)
{
  unsigned int count=0;
  struct pipe*wp,*rp;
  short*rmem,*wmem;
  int size,i;
  float k;
  assert(xmem(t));
  rp=reader((TASK)t);
  wp=writer((TASK)t);
  if(!rp||!wp) return 0;
  size=MIN(read_size(rp),write_size(wp))/2;
  if(!size) return 0;
  rmem=reader_mem(rp);
  wmem=writer_mem(wp);
  k=1.0/(1.0+t->r1+t->r2);
  for(i=0;i<size;i++)
  {
    float out;
    out= (rmem[i]+t->r2*t->x-t->r1*t->y)*k;
    wmem[i]=(short)out;
    t->x=out;
    t->y+=out;
  }
  consume(rp,size*2);
  produce(wp,size*2);
  count+=size*2;
  return count;
}

/*
 ***********************************************************
 */

struct task_delta 
{
  struct task t;
  float w; /* width */
};

unsigned int
task_delta_send(struct task_delta *t);

struct task*
task_delta_new(float w /* inverse gain */)
{
  struct task_delta*t;
  t=(struct task_delta*)xcalloc(sizeof(struct task_delta));
  task_init((TASK)t,NULL,(SEND)task_delta_send,NULL);
  t->w=w;
  return (TASK)t;
}

/* #define DEBUG_LEVEL 1 */
unsigned int
task_delta_send(struct task_delta *t)
{
  unsigned int count=0;
  struct pipe*wp,*rp;
  short*rmem,*wmem;
  int size,i, rsz, wsz;
  assert(xmem(t));
  rp=reader((TASK)t);
  wp=writer((TASK)t);
  if(!rp||!wp) return 0;
  rsz=read_size(rp)/2;
  wsz=write_size(wp)/2;
  DBM(1,printf("delta_send: rsz=%d, wsz=%d\n",rsz,wsz));
  if(rsz<2)
  {
    rsz=reader_request(rp,4)/2;
    if(rsz<2) return 0;
  }
  if(wsz==0)
  {
    return 0;
  }
  size=MIN(rsz,wsz);
  rmem=reader_mem(rp);
  wmem=writer_mem(wp);
  for(i=0;i+1<rsz && i<wsz;i++)
    wmem[i]=(float)(rmem[i+1]-rmem[i])/t->w;
  assert(i);
  consume(rp,i*2);
  produce(wp,i*2);
  count+=i*2;

  return count;
}

/*
 ***********************************************************
 */

/* resonant lowpass */
struct task_rlo1 
{
  struct task t;
  float r; /* 0.0 <= r < 1.0 */
  float x; /* wmem[i-1] */
  float dx;
  float c; /* constant */
};

unsigned int
task_rlo1_send(struct task_rlo1*t);

void
task_rlo1_set_r(struct task*t,float r)
{
  assert(r>=0.0); assert(r<1.0);
  ((struct task_rlo1*)t)->r=r;
}

void
task_rlo1_set_f(struct task*t,float f)
{
  assert(f>0.0);
  ((struct task_rlo1*)t)->c=2.0-2.0*cos(2.0*M_PI*f/44100.0);
}

struct task*
task_rlo1_new( float f, float r )
{
  struct task_rlo1*t;
  t=(struct task_rlo1*)xcalloc(sizeof(struct task_rlo1));
  task_init((TASK)t,NULL,(SEND)task_rlo1_send,NULL);
  task_rlo1_set_r((TASK)t,r);
  task_rlo1_set_f((TASK)t,f);
  t->x=0.0;
  t->dx=0.0;
  return (TASK)t;
}

unsigned int
task_rlo1_send(struct task_rlo1*t)
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
  {
    t->dx+=((float)rmem[i]-t->x)*t->c;
    t->x+=t->dx;
    t->dx*=t->r;
    wmem[i]=(short)(t->x); 
    /* printf("t->x=%.2f\n",t->x); */
  }
  consume(rp,size*2);
  produce(wp,size*2);
  count+=size*2;
  return count;
}

/*
 ***********************************************************
 */

/* resonant lowpass */
struct task_rlo2 
{
  struct task t;
  /* int dummy[128]; */
  float r; /* 0.0 <= r < 1.0 */
  float x; /* wmem[i-1] */
  float dx;
  float cf;
  float c; /* constant */
};

unsigned int
task_rlo2_send(struct task_rlo2*t);

void
task_rlo2_set_r(struct task*_t,float r)
{
  struct task_rlo2*t=(struct task_rlo2*)_t;
  t->r=(sqrt(2)*sqrt(-pow(t->cf-1,3.0))+r*(t->cf-1))/(r*(t->cf-1));
  printf("set_r: t->x=%.2f t->dx=%.2f t->r=%.2f t->c=%.2f \n",
    t->x,t->dx,t->r,t->c);  
}

void
task_rlo2_set_f(struct task*_t,float f)
{
  struct task_rlo2*t=(struct task_rlo2*)_t;
  t->cf=cos(2*M_PI*f/44100.0);
  t->c=2-2*t->cf;
  printf("set_f: t->x=%.2f t->dx=%.2f t->r=%.2f t->c=%.2f \n",
    t->x,t->dx,t->r,t->c);  
}

struct task*
task_rlo2_new( float f, float r )
{
  struct task_rlo2*t;
  t=(struct task_rlo2*)xcalloc(sizeof(struct task_rlo2));
  task_init((TASK)t,NULL,(SEND)task_rlo2_send,NULL);
  task_rlo2_set_r((TASK)t,r);
  task_rlo2_set_f((TASK)t,f);
  t->x=0.0;
  t->dx=0.0;
  return (TASK)t;
}

unsigned int
task_rlo2_send(struct task_rlo2*t)
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
  {
    t->dx+=((float)rmem[i]-t->x)*t->c;
    t->x+=t->dx;
    t->dx*=t->r;
    wmem[i]=(short)(t->x); 
  }
  printf("t->x=%.2f t->dx=%.2f t->r=%.2f t->c=%.2f \n",
    t->x,t->dx,t->r,t->c);  
  if(isnan(t->x)) exit(127);
  consume(rp,size*2);
  produce(wp,size*2);
  count+=size*2;
  return count;
}

/*
 ***********************************************************
 */

struct task_lookup
{
  struct task t;
  struct buffer*b;
  struct pipe*rp;
};

unsigned int
task_lookup_send(struct task_lookup*t)
{
  short*lookup;
  short*rmem;
  short*wmem;
  struct pipe*rp,*wp;
  int sz, i;
  short zero;

  assert( xmem(t) );
  if ( read_size(t->rp) < (1<<17) )
    return 0;
  rp = reader((TASK)t); if (!rp) return 0;
  wp = writer((TASK)t); if (!wp) return 0;
  lookup = (short*)reader_mem(t->rp);
  sz = MIN( read_size(rp), write_size(wp) )/2;
  if(!sz) return 0;
  wmem = (short*)writer_mem(wp);
  rmem = (short*)reader_mem(rp);
  lookup += (1<<15);
  zero = lookup[0];
  for(i=0;i<sz;i++)
  {
    /* int j = ((int)rmem[i]) + (1<<15); */
    int j = rmem[i];
    assert( j+(1<<15) >= 0 );
    assert( j+(1<<15) < read_size(t->rp)/2 );
    wmem[i] = lookup[j] - zero;
  }
  consume(rp,i*2);
  produce(wp,i*2);

  return i*2;
}

void
task_lookup_flush(struct task*t)
{
  assert( xmem(t) );
  consume( ((struct task_lookup*)t)->rp, 1<<17 );
}

void
task_lookup_free(struct task_lookup*t)
{
  /* close_reader(t->rp); */
  pipe_detach(t->rp);
  pipe_free(t->rp);
}

struct task*
task_lookup_new(struct buffer*b)
{
  struct task_lookup*t;
  t=(struct task_lookup*)xcalloc(sizeof(struct task_lookup));
  task_init((TASK)t,NULL,(SEND)task_lookup_send,(FREE)task_lookup_free);
  t->b=b;
  t->rp=reader_new(b);
  return (TASK)t;
}



