#!/usr/bin/python
import os,sys,getopt
import hashlib

def usage():
    print('diff.py [options] directory1 directory2')
    print('  options:')
    print('  -c|--compare-md5: comare md5, very slow!')
    print('  -a|--print-all: print all match result, default only print U|L|R|S!')  
    print('                  L: exist in directory1 not exist in directory2') 
    print('                  R: exist in directory2 not exist in directory1')  
    print('                  M: exist in directory1 and directory2, length/content match(compare md5)') 
    print('                  U: exist in directory1 and directory2, length/content mismatch(compare md5)')
    print('                  S: suspicious file, error when open or read')    
    print('  -h|--help: show this message') 
    
def get_md5(file_path):
    m = hashlib.md5()
    with open(file_path, 'r') as f:
        m.update(f.read())
    return m.hexdigest()
     
    
def compare_file(left, right, use_md5): 
    try:
        if os.path.exists(right) :
            size_left = os.path.getsize(left)
            size_right = os.path.getsize(right)
            if size_left == size_right and not use_md5:
                return 'M'
            elif size_left != size_right:
                return 'U'
            else:
                md5_left = get_md5(left);
                md5_left = get_md5(right);
                if md5_left == md5_right:
                    return 'M'
                else:
                    return 'U'
        else:
            return 'L'
    except Exception:
        return 'S'
    pass
    
def main(argv) :
    options_hash = {'compare-md5':False, 'print-all':False}
    result_hash = {} # rev_path : M|U|L|R 
    try:
        opts,args = getopt.getopt(argv[1:], 'hca', ['help', 'compare-md5', 'print-all'])
        for opt,arg in opts:
            if opt in ('-h', '--help'):
                print('show help')
                usage()
                sys.exit(0)
            elif opt in ('-c', '--compare-md5'):
                options_hash['compare-md5'] = True
            elif opt in ('-a', '--print-all'):
                options_hash['print-all'] = True
                
        if len(args) != 2:
            usage()
            sys.exit(1)
        else:
            dir_from = args[0]
            dir_to = args[1]
            print('dir_from is %s, dir_to is %s' % (dir_from, dir_to))
            print('options is %s' % (options_hash))
    except getopt.GetoptError:
        usage()
        sys.exit(1)
        
    for dirpath,dirnames,filenames in os.walk(dir_from):    
        for filename in filenames:
            left_path = os.path.join(dirpath,filename)
            rev_path = os.path.relpath(left_path, dir_from)
            right_path = os.path.join(dir_to,rev_path)
            result_hash[rev_path] = compare_file(left_path, right_path, options_hash['compare-md5'])
            
    for dirpath,dirnames,filenames in os.walk(dir_to):    
        for filename in filenames:
            right_path = os.path.join(dirpath,filename)
            rev_path = os.path.relpath(right_path, dir_to)
            if not rev_path in result_hash:
                result_hash[rev_path] = 'R'
    
    for file in sorted(result_hash):
        if result_hash[file] == 'M' and options_hash['print-all']:
            print("%s,%s" % (result_hash[file], file))
        elif result_hash[file] != 'M':
            print("%s,%s" % (result_hash[file], file))
        
main(sys.argv)