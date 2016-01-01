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

#ifndef __DEBUG_H
#define __DEBUG_H

#ifdef HAVE_EXECINFO
#include <execinfo.h>
#endif

void show_stackframe();

#if 1
extern int stack;
#define ENTER() (stack++)
#define LEAVE() (stack--)

#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL 0
#endif

#define DBM(n,m) \
{\
  if(DEBUG_LEVEL>=n)\
  {\
    printf("%*c",stack*2,' ');\
    m;\
    fflush(stdout);\
  }\
}

#else

#define ENTER() 
#define LEAVE() 

#define DBM(n,m) 
#endif

#endif /* __DEBUG_H */

