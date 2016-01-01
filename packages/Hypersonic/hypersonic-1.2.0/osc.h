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

#ifndef __OSC_H
#define __OSC_H

void
task_tri_set_f(struct task*t,float f);
void
task_tri_set_r(struct task*t,float r);
struct task*
task_tri_new(float f,float r);
void
task_squ_set_f(struct task*t,float f);
void
task_squ_set_r(struct task*t,float r);
struct task*
task_squ_new(float f,float r);

struct task_sin;

void
task_sin_set_p(struct task*_t,float p);
void
task_sin_set_f(struct task*t,float f);
void
task_sin_set_r(struct task*t,float r);
struct task*
task_sin_new(float freq,float r);

unsigned int
task_noise_send(struct task*t);
SIMPLE_TASK_DEF(noise);

#ifdef BUZZING_SOUNDS
struct task*
task_vdp_new(float e);

struct task*
task_chaos_new(float cx, float cy);
void
task_chaos_set_c(struct task*_t,float cx, float cy);
#endif

struct task*
task_poly_new(int nv, float r, int nu, float alpha );
void
task_poly_set_alpha(struct task*_t, float alpha);
void
task_poly_set_r(struct task*_t, float r);
void
task_poly_set_v(struct task*t, int i,float x);
float
task_poly_get_v(struct task*t, int i);

#endif
