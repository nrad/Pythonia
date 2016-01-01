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
#include <curses.h>
#include <signal.h>
#include <assert.h>
#include "memory.h"
#include "task.h"

struct task_term
{
  struct task t;
};

unsigned int
task_term_send(struct task_term*t)
{
  unsigned int count=0;
  int c;
  /* c=getch(); */
  /* write( 3, ".\n", 2 ); */
  for(c=getch();c!=ERR;c=getch())
  {
    struct pipe*wp;
    int sz;
    char*mem;
    /* got one */
    /* beep(); */
    /* printf("task_term_send: c='%c'\n",c); */
    /* write( 3, "\n", 1 ); */
    wp=writer((TASK)t); if (wp==NULL) return count;
    sz=write_size(wp); if (sz==0) return count;
    /* write( 3, &c, 1 );  */
    mem=writer_mem(wp);
    mem[0]=c; count++;
    produce(wp,1);
  }

  return count;
}

void
task_term_set_line(struct task*_t,int i,char*line)
{
  mvaddstr(i,0,line);
  clrtoeol();
  refresh();
}

static void
finish(int sig)
{
  nocbreak();
  keypad(stdscr,FALSE);
  echo();
  endwin();
}

void
task_term_free(struct task_term*t)
{
  finish(0);
}

struct task*
task_term_new()
{
  struct task_term*t;
  t=(struct task_term*)xcalloc(sizeof(struct task_term));
  task_init((TASK)t,NULL,(SEND)task_term_send,(FREE)task_term_free);

  /* signal(SIGINT,finish); */
  if(initscr()==NULL)
  {
    perror("initscr");
    exit(EXIT_FAILURE);
  }
  keypad(stdscr,TRUE);
  nonl();
  cbreak();
  noecho();
  nodelay(stdscr,TRUE);
  mvaddstr(0,0,"      This is HyperSonic");
  refresh();

  return (TASK)t;
}


