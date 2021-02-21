from Plugins.Plugin import PluginDescriptor
from threading import Thread
import errno
import os
import posix
import traceback
from threading import Thread
import sys


def run_server():
	sys.stderr.write("RunScript started server\n")
	while True:
		try:
			fifo = open('/tmp/run_script.fifo', 'r')
		except IOError:
			return
		commands = fifo.read().strip().split('\n')
		try:
			for command in commands:
				sys.stderr.write("RunScript running: %s\n" % command)
				if command == 'quit':
					return
				if not command:
					continue
				with open(command, 'r') as script_fp:
					script = script_fp.read()
				exec(script)
		except Exception as e:
			traceback.print_exc()


def autostart(reason, **kwargs):
	sys.stderr.write("RunScript %d\n" % reason)
	if reason == 0:
		try:
			os.mkfifo('/tmp/run_script.fifo', 0o666)
		except OSError:
			pass
		thread = Thread(target=run_server)
		thread.start()
	elif reason == 1:
		try:
			fp = posix.open('/tmp/run_script.fifo', posix.O_WRONLY | posix.O_NONBLOCK)
			os.write(fp, 'quit\n')
			posix.close(fp)
		except OSError:
			pass







def Plugins(**kwargs): 
	return PluginDescriptor(name="Run script", description="Run script form /tmp/run_script.fifo", where=PluginDescriptor.WHERE_AUTOSTART, fnc=autostart)