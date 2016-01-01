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



