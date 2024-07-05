#!/usr/bin/python
import os,subprocess,sys,getopt

# global conf
##############################################
rar_cmd = r'C:\Program Files\WinRAR\rar.exe'
unlockrar_cmd = r'D:\Lab\archivetool\RAR Unlocker.exe'
file_stdout = r'stdout.log'
file_stderr = r'stderr.log'
file_status = r'status.log'

#############################################

def test_rar_recover(pathname):
    with open(pathname, 'rb') as f:
        data = f.read(12)
    b = bytearray(data)
    if len(b) == 12:
        if (b[10] & 0x40) != 0:
            return 1
    return 0


def list_nonrar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        fstatus.write('skip,%s\n' % (pathname))
    else :
        print('%s' % pathname)
        fstatus.write('notrar,%s\n' % (pathname))

def unlock_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([unlockrar_cmd, '--unlock', pathname], stdout=fstdout, stderr=fstderr, shell=False)
        print('unlocking %s : %d' % (pathname, status))
        fstatus.write('%d,%s\n' % (status, pathname))
    else:
        fstatus.write('skip,%s\n' % (pathname))

def lock_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([rar_cmd, 'k', pathname], stdout=fstdout, stderr=fstderr, shell=False)
        print('locking %s : %d' % (pathname, status))
        fstatus.write('%d,%s\n' % (status, pathname))
    else:
        fstatus.write('skip,%s\n' % (pathname))

def test_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([rar_cmd, 't', pathname], stdout=fstdout, stderr=fstderr, shell=False)
        print('testing %s : %d' % (pathname, status))
        fstatus.write('%d,%s\n' % (status, pathname))
    else:
        fstatus.write('skip,%s\n' % (pathname))

def addrecover_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    rropt = '-rr%dp' % (option['recovery_percent'])
    if ext[1].upper() == '.RAR':
        if option['force'] or test_rar_recover(pathname) == 0 :
            status = subprocess.call([rar_cmd, rropt, pathname], stdout=fstdout, stderr=fstderr, shell=False)
            print('adding recover record %s : %d' % (pathname, status))
            fstatus.write('%d,%s\n' % (status, pathname))
        else:
            fstatus.write('skip,%s\n' % (pathname))
    else:
        fstatus.write('skip,%s\n' % (pathname))

def create_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    rropt = '-rr%dp' % (option['recovery_percent'])
    volopt = '-v' + option['volume_size']
    if ext[1].upper() != '.RAR' and pathname.upper() != file_status.upper() and pathname.upper() != file_stdout.upper() and pathname.upper() != file_stderr.upper():
        rar_name = ext[0] + '.rar'
        status = subprocess.call([rar_cmd, 'a', rropt, volopt, '-ep', '-o-', '-df', rar_name, pathname], stdout=fstdout, stderr=fstderr, shell=False)
        print('create archive %s : %d' % (pathname, status))
        fstatus.write('%d,%s\n' % (status, pathname))
    else:
        fstatus.write('skip,%s\n' % (pathname))

def usage():
    print('archive.py cmd <options> directory')
    print('    test: test if rar files corrupted')
    print('    lock: lock rar files')
    print('    unlock: unlock rar files')
    print('    addrecover <-f|-force> <-r|--recovery-percent=num>, add recovery information:')
    print('        default not forced, recovery percent 5')
    print('    create <-r|--recovery-percent=num> <-v|--volume-size=num|kKmMgG>: make all non-rar files into rar')
    print('        default recovery percent 1, volume size 2g')
    print('    listnonrar: find all non rar files')

def main(argv) :
    global file_stdout, file_stderr, file_status
    fun_hash = {
    'test' : test_rar, 
    'lock' : lock_rar, 
    'unlock': unlock_rar, 
    'addrecover' : addrecover_rar, 
    'create': create_rar, 
    'listnonrar': list_nonrar}
    options_hash = {'volume_size':'2g', 'force':False, 'recovery_percent':15}
    try:
        opts,args = getopt.getopt(sys.argv[2:], 'v:r:hf', ['volume-size=','recovery-percent=','help', 'force'])
        for opt,arg in opts:
            if opt in ('-h', '--help'):
                print('show help')
                usage()
                sys.exit(0)
            elif opt in ('-v', '--volume-size'):
                options_hash['volume_size'] = arg
            elif opt in ('-f', '--force'):
                options_hash['force'] = True
            elif opt in ('-r', '--recovery-percent'):
                options_hash['recovery_percent'] = int(arg)
            else:
                print('unknown option %s' % (opt))
                usage()
                sys.exit(1)

        if len(args) != 1 or not argv[1] in fun_hash:
            usage()
            sys.exit(1)
        else:
            directory = args[0]
            cmd = argv[1]
            print('directory is %s, cmd is %s' % (directory, cmd))
            print('options is %s' % (options_hash))
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    
    log_stdout = open(file_stdout, 'w')
    log_stderr = open(file_stderr, 'w')
    log_status = open(file_status, 'w')
    
    for dirpath,dirnames,filenames in os.walk(directory):
        for file in filenames:
            fullpath=os.path.join(dirpath,file)
            fun_hash[argv[1]](fullpath, log_stdout, log_stderr, log_status, options_hash)

    log_status.close()
    log_stdout.close()
    log_stderr.close()


main(sys.argv)