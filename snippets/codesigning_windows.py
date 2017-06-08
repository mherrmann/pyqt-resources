from os.path import join, splitext
from subprocess import call, DEVNULL, Popen, STDOUT, CalledProcessError

import os

def sign_exe():
	for subdir, _, files in os.walk(path('target/fman')):
		for file_ in files:
			extension = splitext(file_)[1]
			if extension in ('.exe', '.cab', '.dll', '.ocx', '.msi', '.xpi'):
				file_path = join(subdir, file_)
				if not _is_signed(file_path):
					_sign(file_path)

def add_installer_manifest():
	"""
	If an .exe name contains "installer", "setup" etc., then at least Windows 10
	automatically opens a UAC prompt upon opening it. This can be avoided by
	adding a compatibility manifest to the .exe.
	"""
	run([
		'mt.exe', '-manifest', path('src/main/fmanSetup.exe.manifest'),
		'-outputresource:%s;1' % path('target/fmanSetup.exe')
	])

def sign_installer():
	_sign(path('target/fmanSetup.exe'), 'fman Setup', 'https://fman.io')

def _is_signed(file_path):
	return not call(
		['signtool', 'verify', '/pa', file_path], stdout=DEVNULL, stderr=DEVNULL
	)

def _sign(file_path, description='', url=''):
	args = [
		'signtool', 'sign', '/f', path('YOUR_PFX_FILE.pfx'),
		'/p', 'PFX_FILE_PW', '/tr', 'http://tsa.startssl.com/rfc3161'
	]
	if description:
		args.extend(['/d', description])
	if url:
		args.extend(['/du', url])
	args.append(file_path)
	_run(args)
	args_sha256 = \
		args[:-1] + ['/as', '/fd', 'sha256', '/td', 'sha256'] + args[-1:]
	_run(args_sha256)

def _run(cmd, extra_env=None, check_result=True, cwd=None):
	if extra_env:
		env = dict(os.environ)
		env.update(extra_env)
	else:
		env = None
	process = Popen(cmd, env=env, stderr=STDOUT, cwd=cwd)
	process.wait()
	if check_result and process.returncode:
		raise CalledProcessError(process.returncode, cmd)