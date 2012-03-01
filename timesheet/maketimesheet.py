#!/usr/bin/env python
from timesheet.models import Entry
def skipfields(s, offset, n):
	for j in range(0,n):
		while s[offset] != 'F':
			offset += 1
		offset += 1
	return offset-1
	
def writeentry(s, offset, step, e):
        fields = (
                "%i" % e.get_weeknumber(),
                e.get_shortdatestring(),
                e.start_time.__str__()[:5],
                e.end_time.__str__()[:5],
                "% 2.2f" % e.get_timediff(),
                )
	for field in fields:
		offset += 11*step
		for c in field:
			s[offset] = c
			offset += step
		offset = skipfields(s, offset, 1)
	return offset
def make_timesheet(filename, timesheet):	
    entrylist = timesheet.entry_set.all()
    fd = open(filename,'rb')
    s = fd.read()
    fd.close()
    s = list(s)
    offset = 0x0b93
    step = 1
    n = 3
    i = 0
    for e in entrylist:
        if not s[offset] == 'F': 
            exit(1)

	if s[offset+1] == 'O':
            step = 1
	else:
            step = 2
	offset = writeentry(s, offset, step, e)
	offset = skipfields(s,offset,11-5)
	i+=1

    s = ''.join(s)
    return s
