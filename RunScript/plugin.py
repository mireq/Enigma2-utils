from Plugins.Plugin import PluginDescriptor
from contextlib import contextmanager
from threading import Thread
import errno
import os
import posix
import sys
import traceback


@contextmanager
def redirect_stdout(new_target):
	if new_target is None:
		yield new_target
	else:
		old_stdout, old_stderr = sys.stdout, sys.stderr

		try:
			sys.stdout, sys.stderr = new_target, new_target
			yield new_target
		finally:
			sys.stdout, sys.stderr = old_stdout, old_stderr


def run_server(session):
	sys.stderr.write("RunScript started server\n")

	while True:
		try:
			fifo = open('/tmp/run_script.fifo', 'r')
		except IOError:
			return

		commands = fifo.read().strip().split('\n')

		try:
			output = posix.open('/tmp/run_script_output.fifo', posix.O_WRONLY | posix.O_NONBLOCK)
			output = os.fdopen(output, 'w')
		except OSError:
			output = None

		with redirect_stdout(output):
			try:
				for command in commands:
					sys.stderr.write("RunScript running: %s\n" % command)
					if command == 'quit':
						return
					if not command:
						continue
					with open(command, 'r') as script_fp:
						script = script_fp.read()
					exec(script, {'session': session})
			except Exception as e:
				traceback.print_exc()

		if output is not None:
			output.close()


def autostart(reason, **kwargs):
	sys.stderr.write("RunScript %d\n" % reason)
	if reason == 0:
		session = kwargs.get('session')
		sys.stderr.write("RunScript %s\n" % session)
		if session is None:
			return
		try:
			os.mkfifo('/tmp/run_script.fifo', 0o666)
		except OSError:
			pass
		try:
			os.mkfifo('/tmp/run_script_output.fifo', 0o666)
		except OSError:
			pass
		thread = Thread(target=run_server, args=(kwargs.get('session'),))
		thread.start()
	elif reason == 1:
		try:
			fp = posix.open('/tmp/run_script.fifo', posix.O_WRONLY | posix.O_NONBLOCK)
			os.write(fp, 'quit\n')
			posix.close(fp)
		except OSError:
			pass


def Plugins(**kwargs):
	return PluginDescriptor(name="Run script", description="Run script form /tmp/run_script.fifo", where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart)
