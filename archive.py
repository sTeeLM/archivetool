#!/usr/bin/python
import os,subprocess,sys,getopt
import subprocess
# global conf
##############################################
rar_cmd = r'C:\Program Files\WinRAR\rar.exe'
unlockrar_cmd = r'D:\Lab\archivetool\RAR Unlocker.exe'
file_stdout = r'stdout.log'
file_stderr = r'stderr.log'
file_status = r'status.log'
file_continue = r'continue.log'
##############################################

# global const
##############################################
STATUS_OK   = 0
STATUS_FAIL = 1
STATUS_SKIP = -1
##############################################


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
        fstatus.write('%d,%s\n' % (status, pathname))
        if status != 0:
            status = STATUS_FAIL;
        else:
            status = STATUS_OK;
    else:
        status = STATUS_SKIP
    return status
    

def lock_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([rar_cmd, 'k', pathname], stdout=fstdout, stderr=fstderr, shell=False)
        fstatus.write('%d,%s\n' % (status, pathname))
        if status != 0:
            status = STATUS_FAIL;
        else:
            status = STATUS_OK;
    else:
        status = STATUS_SKIP
    return status

def test_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([rar_cmd, 't', pathname], stdout=fstdout, stderr=fstderr, shell=False)
        fstatus.write('%d,%s\n' % (status, pathname))
        if status != 0:
            status = STATUS_FAIL;
        else:
            status = STATUS_OK;
    else:
        status = STATUS_SKIP
    return status

def addrecover_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    rropt = '-rr%dp' % (option['recovery_percent'])
    if ext[1].upper() == '.RAR':
        if option['force'] or test_rar_recover(pathname) == 0 :
            status = subprocess.call([rar_cmd, rropt, pathname], stdout=fstdout, stderr=fstderr, shell=False)
            fstatus.write('%d,%s\n' % (status, pathname))
            if status != 0:
                status = STATUS_FAIL;
            else:
                status = STATUS_OK;
        else:
            status = STATUS_SKIP
    else:
        status = STATUS_SKIP
    return status

def create_rar(pathname, fstdout, fstderr, fstatus, option):
    ext = os.path.splitext(pathname)
    rropt = '-rr%dp' % (option['recovery_percent'])
    volopt = '-v' + option['volume_size']
    if ext[1].upper() != '.RAR':
        rar_name = ext[0] + '.rar'
        status = subprocess.call([rar_cmd, 'a', rropt, volopt, '-ep', '-o-', '-df', rar_name, pathname], stdout=fstdout, stderr=fstderr, shell=False)
        fstatus.write('%d,%s\n' % (status, pathname))
        if status != 0:
            status = STATUS_FAIL;
        else:
            status = STATUS_OK;
    else:
        status = STATUS_SKIP
    return status

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
    file_list = []
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
    
    log_stdout = open(file_stdout, 'a')
    log_stderr = open(file_stderr, 'a')
    log_status = open(file_status, 'a')
    
    continue_index = 0;
    
    try:
        with open(file_continue, 'r') as continue_file:
            continue_index = continue_file.read()
            continue_index = int(continue_index)
    except Exception:
        continue_index = 0
    
    total_size = 0
    done_size  = 0
    for dirpath,dirnames,filenames in os.walk(directory):
        for file in filenames:
            fullpath = os.path.join(dirpath,file)
            file_size = os.path.getsize(fullpath)
            file_list.append((fullpath, file_size))
            total_size += file_size;
    
    file_list.sort()
    
    current_index = 0
    if cmd != 'listnonrar' :
        print('continue index is %d' % continue_index)
        for pathname,file_size in file_list:
            if current_index < continue_index:
                current_index += 1
                done_size += file_size;
                progress = int(done_size * 100 / total_size)
                print('continue \x1b[33mSKIP\x1b[m [%03d%%]: %s' % (progress, pathname))
                continue
            status = fun_hash[argv[1]](pathname, log_stdout, log_stderr, log_status, options_hash)
            done_size += file_size;
            progress = int(done_size * 100 / total_size)
            if status == STATUS_OK:
                print('%s \x1b[32mOK  \x1b[m [%03d%%]: %s' % (cmd, progress, pathname))
            elif status == STATUS_SKIP:
                print('%s \x1b[33mSKIP\x1b[m [%03d%%]: %s' % (cmd, progress, pathname))
            else:
                print('%s \x1b[31mFAIL\x1b[m [%03d%%]: %s' % (cmd, progress, pathname))
            current_index += 1
            log_status.flush()
            log_stdout.flush()
            log_stderr.flush()
            try:
                with open(file_continue, 'w') as continue_file:
                    continue_file.write(str(current_index))
                    continue_file.flush()
            except Exception:
                pass
    else:
        for pathname,file_size in file_list: # list_nonrar
            fun_hash[argv[1]](pathname, log_stdout, log_stderr, log_status, options_hash)
            
    log_status.close()
    log_stdout.close()
    log_stderr.close()

subprocess.call('', shell=True)
main(sys.argv)