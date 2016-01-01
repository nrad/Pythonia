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

#ifndef __ARRAY_H
#define __ARRAY_H

#include <stddef.h>

struct array
{
  void*mem;
  int sz;
  void (*free)(struct array*);
  struct array*a; /* parent */
  int refc; 
  /*struct array *next, *prev;*/

  /* multidimensional ? */ 
  /* int *dim; */
  /* int *pitch;  */
};

typedef void (*A_FREE)(struct array*);

/* void array_init(struct array*a,A_FREE free); */

struct array*
array_new(int sz);
struct array*
array_new_mmap(char*filename);
struct array*
array_new_sub(struct array*a,int _i,int i);
void*
array_mem(struct array*a);
int
array_sz(struct array*a);
void
array_set_short(struct array*a, int i, short x);
short
array_get_short(struct array*a, int i);

void
array_free(struct array*a);

#endif
