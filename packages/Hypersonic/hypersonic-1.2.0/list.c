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

/**
 * The circular doubly linked implementation is based upon algorithm
 * described in Knuth's The Art of Computer Programing, Vol 1,
 * section 2.2.5. 
 */

#include <assert.h>
#include <stdlib.h>
#include "list.h"

#define list_top(l)      (l->k.rk)
#define list_bottom(l)   (l->k.lk)

void
list_init(struct list *l)
{
  l->k.rk = &l->k;
  l->k.lk = &l->k;
}

void  
list_insert_after(struct list *l, void *anchorp, void *kp)
{
  struct link *anchor = (struct link *)anchorp;
  struct link *k = (struct link *)kp; 

  assert(k->lk==NULL);
  assert(k->rk==NULL);

  if (list_empty(l))
    anchor = &l->k;
  k->lk = anchor;
  k->rk = anchor->rk;
  anchor->rk->lk = k;
  anchor->rk = k;
}

void  
list_insert_before(struct list *l, void *anchorp, void *kp)
{
  struct link *anchor = (struct link *)anchorp;
  struct link *k = (struct link *)kp; 

  assert(k->lk==NULL);
  assert(k->rk==NULL);

  if (list_empty(l))
    anchor = &l->k;
  k->rk = anchor;
  k->lk = anchor->lk;
  anchor->lk->rk = k;
  anchor->lk = k;
}

void  
list_append(struct list *l, void *k)
{
  list_insert_after(l, list_bottom(l), k);
  assert( list_last(l) == k );
}

void
list_prepend(struct list *l, void *k)
{
  list_insert_before(l, list_top(l), k);
  assert( list_first(l) == k );
}

void  
list_remove(struct list *l, void *kp)
{
  struct link *k = (struct link *)kp; 

  assert(list_has(l,k));
  k->lk->rk = k->rk;
  k->rk->lk = k->lk;
  k->rk = k->lk = 0;
}

void *
list_pop(struct list *l) 
{
  void *k = list_last(l);
  if (k != 0)
    list_remove(l, k);
  return k;
}  

void * 
list_first(struct list *l)
{
  if (list_empty(l))
    return 0;
  return list_top(l);
}

void * 
list_last(struct list *l)
{
  if (list_empty(l))
    return 0;
  return list_bottom(l);
}

void * 
list_next(struct list *l, void *kp)
{
  struct link *k = (struct link *)kp; 
  if (k == list_bottom(l))
    return 0;
  return k->rk;
}

void * 
list_prev(struct list *l, void *kp)
{
  struct link *k = (struct link *)kp; 
  if (k == list_top(l))
    return 0;
  return k->lk;
}

void
list_iterate(struct list*l, void (*f)(void*))
{
  struct link*k;
  for(k=(struct link*)list_first(l);k;k=(struct link*)list_next(l,k))
    (*f)(k);
}

int
list_has(struct list*l,struct link*_k )
{
  struct link*k;
  for(k=(struct link*)list_first(l);k;k=(struct link*)list_next(l,k))
    if(_k==k) return 1;
  return 0;
}

#define _STANDALONE 
#ifdef STANDALONE

int _main(void)
{
  struct item
  {
    struct link k;
    struct link _k; /* no */
    int i;
#define NITEMS 10
  } items[NITEMS];
  int i;
  struct link k={0,0};
  for(i=0;i<NITEMS;i++)
  {
    items[i].k=items[i]._k=k;
    items[i].i=i;
  }
  return 0;
}

int main(void)
{
  struct item
  {
    struct link k;
    int a;
  };

  struct item a = { {0,0}, 1 };
  struct item b = { {0,0}, 2 };
  struct item c = { {0,0}, 3 };
  struct item d = { {0,0}, 4 };
  struct item e = { {0,0}, 5 };
  struct item f = { {0,0}, 0 };

  struct list l = { {0,0} };

  struct item *ptr = 0;

  list_init(&l);
  list_append(&l, &b);
  list_insert_before(&l, &b, &a);
  list_insert_after(&l, &b, &d);
  list_insert_after(&l, &b, &c);
  list_append(&l, &e);
  list_prepend(&l, &f);

  for (ptr = (struct item *)list_first(&l);
      ptr != 0;
      ptr = (struct item *)list_next(&l, ptr))
    printf("%d\n", ptr->a);

  list_remove(&l, &f);
  list_remove(&l, &e);
  list_remove(&l, &b);
  list_remove(&l, &c);
  for (ptr = (struct item *)list_last(&l);
      ptr != 0;
      ptr = (struct item *)list_prev(&l, ptr))
    printf("%d\n", ptr->a);
  list_remove(&l, &d);
  list_remove(&l, &a);
  for (ptr = (struct item *)list_first(&l);
      ptr != 0;
      ptr = (struct item *)list_next(&l, ptr))
    printf("%d\n", ptr->a);

  return 0;
}

#endif
