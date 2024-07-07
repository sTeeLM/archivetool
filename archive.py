#!/usr/bin/python
import os
import subprocess
import sys
import getopt
import subprocess
# global conf
##############################################
rar_cmd = r'rar.exe'
unlockrar_cmd = r'RAR Unlocker.exe'
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


def list_nonrar(pathname, fstdout, fstderr, fstatus, options):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        fstatus.write('skip,%s\n' % (pathname))
    else :
        print('%s' % pathname)
        fstatus.write('notrar,%s\n' % (pathname))

def unlock_rar(pathname, fstdout, fstderr, fstatus, options):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([unlockrar_cmd, '--unlock', pathname], stdin = None, stdout=fstdout, stderr=fstderr, shell=False)
        fstatus.write('%d,%s\n' % (status, pathname))
        if status != 0:
            status = STATUS_FAIL;
        else:
            status = STATUS_OK;
    else:
        status = STATUS_SKIP
    return status
    

def lock_rar(pathname, fstdout, fstderr, fstatus, options):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([rar_cmd, 'k', pathname], stdin = None, stdout=fstdout, stderr=fstderr, shell=False)
        fstatus.write('%d,%s\n' % (status, pathname))
        if status != 0:
            status = STATUS_FAIL;
        else:
            status = STATUS_OK;
    else:
        status = STATUS_SKIP
    return status

def test_rar(pathname, fstdout, fstderr, fstatus, options):
    ext = os.path.splitext(pathname)
    if ext[1].upper() == '.RAR' :
        status = subprocess.call([rar_cmd, 't', pathname], stdin = None, stdout=fstdout, stderr=fstderr, shell=False)
        fstatus.write('%d,%s\n' % (status, pathname))
        if status != 0:
            status = STATUS_FAIL;
        else:
            status = STATUS_OK;
    else:
        status = STATUS_SKIP
    return status

def addrecover_rar(pathname, fstdout, fstderr, fstatus, options):
    ext = os.path.splitext(pathname)
    rropt = '-rr%dp' % (options['recovery_percent'])
    if ext[1].upper() == '.RAR':
        if options['force'] or test_rar_recover(pathname) == 0 :
            status = subprocess.call([rar_cmd, rropt, pathname], stdin = None, stdout=fstdout, stderr=fstderr, shell=False)
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

def create_rar(pathname, fstdout, fstderr, fstatus, options):
    ext = os.path.splitext(pathname)
    filename = os.path.basename(pathname)
    rropt = '-rr%dp' % (options['recovery_percent'])
    volopt = '-v' + options['volume_size']
    if ext[1].upper() != '.RAR' and filename not in options['exclude']:
        rar_name = ext[0] + '.rar'
        status = subprocess.call([rar_cmd, 'a', rropt, volopt, '-ep', '-o-', '-df', rar_name, pathname], 
            stdin = None, stdout=fstdout, stderr=fstderr, shell=False)
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
    print('    addrecover: add recovery information')
    print('        options: <-f|-force> : force add even have recover record, default false')
    print('                 <-r|--recovery-percent=num> : percent of recover record, default 15')
    print('    create: archive non-rar files into rar')
    print('        options: <-r|--recovery-percent=num> : percent of recover record, default 15')
    print('                 <-v|--volume-size=num|kKmMgG> : volume size, default 2G')
    print('    listnonrar: find all non rar files')



def parse_cmd(argv) :
    cmd_options = {
        'test': {'opts' : 'v', 'lopts' : ['verbose']},
        'lock' : {'opts' : 'v', 'lopts' : ['verbose']},
        'unlock' : {'opts' : 'v', 'lopts' : ['verbose']},
        'addrecover' : {'opts' : 'vfr:', 'lopts' : ['verbose','force','recovery-percent=']},
        'create' : {'opts' : 'vr:e:V:', 'lopts' : ['verbose', 'recovery-percent=', 'exclude=', 'volume-size=']},
        'listnonrar' : {'opts' : 'v', 'lopts' : ['verbose']},
        }
    parsed_options = {
        'verbose' : False,
        'force' : False,
        'recovery-percent' : 15,
        'exclude' : [],
        'volume-size': '2G'
    }
    if len(argv) <= 2:
        usage()
        return (None, None, None)
    if argv[1] in cmd_options :
        try:
            opts, args = getopt.getopt(argv[2:], cmd_options[argv[1]]['opts'], cmd_options[argv[1]]['lopts'])
            for opt,arg in opts :
                if opt in ('-v', '--verbose') :
                    parsed_options['verbose'] = True
                elif opt in ('-f', '--force') :
                    parsed_options['force'] = True
                elif opt in ('-e', '--exclude') :
                    parsed_options['exclude'] = args.split(',')
                elif opt in ('-V', '--volume-size') :
                    parsed_options['volume-size'] = args
                else:
                    usage()
                    return (None, None, None)
            if len(args) != 1 :
                usage()
                return (None, None, None)
        except getopt.GetoptError:
            usage()
            return (None, None, None)
        return (argv[1], parsed_options, args)
    else:
        usage()
        return (None, None, None)

def main(argv) :
    global file_stdout, file_stderr, file_status
    
    fun_hash = {
        'test' : test_rar, 
        'lock' : lock_rar, 
        'unlock': unlock_rar, 
        'addrecover' : addrecover_rar, 
        'create': create_rar, 
        'listnonrar': list_nonrar
    }
    
    cmd, options, args = parse_cmd(argv)
    if not cmd or not options or not args:
        return 1
   
    directory = args[0]
    print('directory is %s, cmd is %s' % (directory, cmd))
    print('options is %s' % (options))
    
    log_stdout = open(file_stdout, 'a', encoding='utf-8')
    log_stderr = open(file_stderr, 'a', encoding='utf-8')
    log_status = open(file_status, 'a', encoding='utf-8')
    
    continue_index = 0;
    
    try:
        with open(file_continue, 'r') as continue_file:
            continue_index = continue_file.read()
            continue_index = int(continue_index)
    except Exception:
        continue_index = 0
    
    total_size = 0
    done_size  = 0
    file_list = []
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
                if options['verbose']:
                    done_size += file_size;
                    progress = int(done_size * 100 / total_size)
                    print('continue \x1b[33mSKIP\x1b[m [%03d%%]: %s' % (progress, pathname))
                continue
            status = fun_hash[argv[1]](pathname, log_stdout, log_stderr, log_status, options)
            if options['verbose']:
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
            fun_hash[argv[1]](pathname, log_stdout, log_stderr, log_status, options)
            
    log_status.close()
    log_stdout.close()
    log_stderr.close()

subprocess.call('', shell=True)
main(sys.argv)