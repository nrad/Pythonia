#!/usr/bin/env python

import sys
import string

def usage():
  print " USAGE :",
  print sys.argv[0],
  print " task_name [ type var ]* "
  sys.exit(0)

args=sys.argv

if len(args)<2: usage()

name=args[1]

vars=[]
args=args[2:]
while len(args)>1:
  vars.append((args[0],args[1]))
  args=args[2:]
if args: usage()

struct="struct task_"+name
#send="unsigned int\ntask_"+name+"_send(struct "+\
#  name+"_task*"+name[0]+"_t)"
#send="unsigned int\ntask_"+name+"_send(struct "+name+"_task*t)"
send="unsigned int\ntask_"+name+"_send("+struct+"*t)"
free="void\ntask_"+name+"_free("+struct+"*t)"

print """
/*
 ***********************************************************
 */
"""
print struct
print "{\n  struct task t;"

for var in vars:
  print "  "+var[0]+" "+var[1]+";"
print "};"
print
#print send+";"
#print
print send
print "{"
#print "  unsigned int count=0;"
#print
#print "  return count;"
print "  return 0;"
print "}"
print
print free
print "{"
print "  assert(xmem(t));"
print "}"
print
print "struct task*"
_vars = map( lambda x: x[0]+" "+x[1], vars )
print "task_"+name+"_new("+string.join(_vars,", ")+")"
print "{"
print "  "+struct+"*t;"
print "  t=("+struct+"*)xcalloc(sizeof("+struct+"));"
print "  task_init((TASK)t,NULL,(SEND)task_"\
      +name+"_send,(FREE)task_"+name+"_free);"
for var in vars:
  print "  t->"+var[1]+"="+var[1]+";"
print "  return (TASK)t;"
print "}"
print

#print vars
