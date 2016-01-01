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

#ifndef __MEMORY_H
#define __MEMORY_H

#define MAKE(type,ident) type*ident=(type*)xcalloc(sizeof(type))

#define MEMORY_CHECK
#ifdef MEMORY_CHECK
#include <stdlib.h>
void*xmalloc(size_t s);
void*xcalloc(size_t s);
void*xrealloc(void*,size_t s);
void xmark();
int xmem(void*);
int xcheck();
void xfree(void*p);
#else
#include <malloc.h>
#define xmalloc(s)	malloc(s)
#define xcalloc(s)	calloc(1,s)
#define xrealloc(p,s)	realloc((p),(s))
#define xmark()		
#define xmem(p)		(1)
#define xcheck()	(0)
#define xfree(p)	free(p)
#endif
#endif
