#!/usr/bin/python
import os,subprocess,sys

# global conf
##############################################
rar_cmd = r"C:\Program Files\WinRAR\rar.exe"
unlockrar_cmd = r"C:\Program Files\WinRAR\RAR Unlocker.exe"
file_stdout = r'C:\Data\Test\stdout.log'
file_stderr = r'C:\Data\Test\stderr.log'
file_status = r'C:\Data\Test\status.log'
#############################################

def find_nonrar(pathname, fstdout, fstderr, fstatus):
	ext = os.path.splitext(pathname)
	if ext[1].upper() == '.RAR' :
		fstatus.write("skip,%s\n" % (pathname))
	else :
		print pathname
		fstatus.write("notrar,%s\n" % (pathname))

def unlock_rar(pathname, fstdout, fstderr, fstatus):
	ext = os.path.splitext(pathname)
	if ext[1].upper() == '.RAR' :
		status = subprocess.call([unlockrar_cmd, "--unlock", pathname], stdout=fstdout, stderr=fstderr, shell=False)
		print "unlocking %s : %d" % (pathname, status)
		fstatus.write("%d,%s\n" % (status, pathname))
	else:
		fstatus.write("skip,%s\n" % (pathname))

def lock_rar(pathname, fstdout, fstderr, fstatus):
	ext = os.path.splitext(pathname)
	if ext[1].upper() == '.RAR' :
		status = subprocess.call([rar_cmd, "k", pathname], stdout=fstdout, stderr=fstderr, shell=False)
		print "locking %s : %d" % (pathname, status)
		fstatus.write("%d,%s\n" % (status, pathname))
	else:
		fstatus.write("skip,%s\n" % (pathname))

def test_rar(pathname, fstdout, fstderr, fstatus):
	ext = os.path.splitext(pathname)
	if ext[1].upper() == '.RAR' :
		status = subprocess.call([rar_cmd, "t", pathname], stdout=fstdout, stderr=fstderr, shell=False)
		print "testing %s : %d" % (pathname, status)
		fstatus.write("%d,%s\n" % (status, pathname))
	else:
		fstatus.write("skip,%s\n" % (pathname))

def addrecover_rar(pathname, fstdout, fstderr, fstatus):
	ext = os.path.splitext(pathname)
	if ext[1].upper() == '.RAR' :
		status = subprocess.call([rar_cmd, "rr5p", pathname], stdout=fstdout, stderr=fstderr, shell=False)
		print "adding recover record %s : %d" % (pathname, status)
		fstatus.write("%d,%s\n" % (status, pathname))
	else:
		fstatus.write("skip,%s\n" % (pathname))

def create_rar(pathname, fstdout, fstderr, fstatus):
	ext = os.path.splitext(pathname)
	if ext[1].upper() != '.RAR' and pathname.upper() != file_status.upper() and pathname.upper() != file_stdout.upper() and pathname.upper() != file_stderr.upper():
		rar_name = ext[0] + '.rar'
		status = subprocess.call([rar_cmd, "a", "-rr5p", "-ep", "-o-", rar_name, pathname], stdout=fstdout, stderr=fstderr, shell=False)
		print "create archive %s : %d" % (pathname, status)
		fstatus.write("%d,%s\n" % (status, pathname))
	else:
		fstatus.write("skip,%s\n" % (pathname))


log_stdout = open(file_stdout,'w')
log_stderr = open(file_stderr,'w')
log_status = open(file_status,'w')

cmd = sys.argv[1]
path= sys.argv[2]


for dirpath,dirnames,filenames in os.walk(path):
	for file in filenames:
		fullpath=os.path.join(dirpath,file)
		if cmd == 'test' :
			test_rar(fullpath, log_stdout, log_stderr, log_status)
		elif cmd == 'lock' :
			lock_rar(fullpath, log_stdout, log_stderr, log_status)
		elif cmd == 'unlock' :
			unlock_rar(fullpath, log_stdout, log_stderr, log_status)
		elif cmd == 'addrecover' :
			addrecover_rar(fullpath, log_stdout, log_stderr, log_status)
		elif cmd == 'create' :
			create_rar(fullpath, log_stdout, log_stderr, log_status)
		elif cmd == 'findnonrar' :
			find_nonrar(fullpath, log_stdout, log_stderr, log_status)

log_status.close()
log_stdout.close()
log_stderr.close()