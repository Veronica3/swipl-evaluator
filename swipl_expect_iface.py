#!/usr/bin/env python3
from __future__ import print_function 
import pexpect
from pipes import quote

class PrologError(Exception):
	pass

def run_swipl(filename, queries):
	queries = list(reversed(queries))
	child = pexpect.spawn('swipl -s ' + quote(filename))

	def sendline(line):
		child.sendline(line)

	def do_query(goal):
		goal = goal.strip()
		if len(list(filter(lambda x: x == ".", goal))) != 1:
			raise PrologError("wrong count \".\" in line: {0}".format(goal))
		sendline("safe_goal({0}).".format(goal[0:len(goal)-1]))
		while 1:
			j = child.expect_exact(["false.", "true.", "false", "true", "\n?- "])
			if j == 0 or j == 2: raise PrologError("\"{0}\" not allowed".format(goal))
			if j == 2 or j == 3: child.send(";")
			if j == 4: break
		sendline(goal)
		

	i=0
	retbuf = ""
	child.expect_exact("\n?- ")
	retbuf += child.before
	#sendline("a(2,X,[1,2]).")
	sendline("use_module('lib_safecode.pl',[safe_goal/1]).")
	child.expect_exact("\n?- ")
	do_query(queries.pop())
	#child.expect_exact("\n?- ")
	buf = "?- "
	dieonnewline = False
	waitoutput=False
	while 1:
		try:
			c = child.read_nonblocking(size=1, timeout=0.1)
		except pexpect.TIMEOUT:
			if waitoutput:
				raise PrologError("Prolog interpreter busy for too long. Missing dot?")
			child.send(";")
			waitoutput=True
			continue
			
		if c != ";": waitoutput=False
		if dieonnewline and c[-1::] == "\n":
			raise PrologError("swipl: " + buf.split("\n")[-1])
		buf += c
		if buf[-6::] == "\nERROR":
			dieonnewline = True
		elif buf[-4::] == "\n?- ":
			if len(queries) == 0: 
				sendline("halt.")
				break
			else:
				do_query(queries.pop())

	retbuf += buf
	retbuf += "\n".join(child.readlines())
	try:
		child.wait()
	except pexpect.ExceptionPexpect:
		pass
	#buf = buf.replace("".join(map(chr,[0x1b, 0x5b, 0x43])), "")
	#buf = ''.join(filter(lambda x:x in list(map(chr,range(ord(' '),ord('~'))))+["\n"], buf))
	return buf

if __name__ == "__main__":
	print(run_swipl("../u8_5",["a(X,[],[1]).","open('/etc/passwd', read, Stream)."]))
