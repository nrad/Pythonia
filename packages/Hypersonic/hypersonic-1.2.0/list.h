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
#ifndef list_h
#define list_h

struct link
{
  struct link *lk, *rk;
};

struct list
{
  struct link k;
};

void   
list_init( struct list *l );
void   
list_append( struct list *l, void *k );
void   
list_prepend( struct list *l, void *k );
void   
list_insert_after( struct list *l, void *anchor, void *k );
void   
list_insert_before( struct list *l, void *anchor, void *k );
void * 
list_first( struct list *l );
void * 
list_last( struct list *l );
void * 
list_next( struct list *l, void *k );
void * 
list_prev( struct list *l, void *k );
void   
list_remove( struct list *l, void *k );
void   
list_push( struct list *l, void *k );
void * 
list_pop( struct list *l );

#define LIST struct list*
#define LINK struct link*
#define ITER void(*)(void*)

void
list_iterate(struct list*,void (*f)(void*));
int
list_has(struct list*,struct link* );

#define list_push(l,k) list_append((l), (k))
#define list_empty(l)    ((l)->k.rk == &(l)->k)

#endif
