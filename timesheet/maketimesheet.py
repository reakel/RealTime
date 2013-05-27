#!/usr/bin/env python
# -*- coding: utf-8 -*-
from timesheet.models import Entry


class GenerateTimeheetError(Exception):
    pass


def skipfields(s, offset, n):
	for j in range(0,n):
		while s[offset] != 'F':
			offset += 1
                        if (s[offset+1] == 'O'):
                            step = 1
                        else: 
                            step = 2
		offset += 1
	return (offset-1,step)
	
def writeentry(s, offset, step, e):
        fields = (
                "%i" % e.get_weeknumber(),
                e.get_shortdatestring(),
                e.start_time.__str__()[:5],
                e.end_time.__str__()[:5],
                "% 2.2f" % e.get_timediff(),
                )
        return write_fields(s, offset, step, fields)

def write_fields(s, offset, step, fields):
    for field in fields:
        field = field.encode('ISO-8859-1')
        offset += 11*step
        for c in field:
            s[offset] = c
            offset += step
        (offset, step) = skipfields(s, offset, 1)
    return (offset, step)


def find(s, offset, find_str):
    found = False
    find_str = find_str.encode('ISO-8859-1')
    while offset < len(s) and not found:
        if s[offset] == find_str[0]:
            if len(find_str) == 1:
                return offset
            if s[offset+1] == find_str[1]:
                step = 1
            elif s[offset+2] == find_str[1]:
                step = 2
            else:
                offset += 1
                continue
            i = 2
            found = True
            while offset+i*step < len(s) and i < len(find_str):
                if s[offset+i*step] != find_str[i]:
                    found = False
                    break
                i += 1
        offset += 1
    if not found: return -1
    return offset-1


"""
def write_field(s, offset, string, step, maxlength):
    for c in string:
        s[offset] = c
        offset += 1
        """
def write_user_info(s,offset,user):
    name = u"%s, %s" % (user.last_name, user.first_name)
    fields = (
            user.get_profile().birth_date[:6],
            user.get_profile().p_no[:5],
            name[:30],
            user.get_profile().skattekommune[:5],
            '',
            '',
            user.get_profile().address[:30],
            '',
            '',
            user.get_profile().zip_code[:4],
            user.get_profile().city[:25],
            user.get_profile().account_number[:11]
            )
    offset = find(s,offset,u'selsdato')
    (offset, step) = skipfields(s, offset, 1)
    return write_fields(s,offset,step,fields)

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
	    raise GenerateTimesheetError('Could not parse timesheet file "%s"' % filename)

	(offset, step) = writeentry(s, offset, step, e)
	(offset,step) = skipfields(s,offset,11-5)
	i+=1
    (offset,step) = write_user_info(s, offset, timesheet.user)

    s = ''.join(s)
    return s
