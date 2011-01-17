"""Utilities used with spatial information
"""
import os
from subprocess import Popen, PIPE
from config import filenames_updated, update_marker
            
def run_old(s, verbose=True):
    if verbose:
        print s
    err = os.system(s)
    return err
    
def run(cmd, 
        stdout=None,
        stderr=None, 
        verbose=True):
        
    s = cmd    
    if stdout:
        s += ' > %s' % stdout
        
    if stderr:
        s += ' 2> %s' % stderr        
        
    if verbose:
        print s
    err = os.system(s)
    
    if err != 0:
        msg = 'Command "%s" failed with errorcode %i. ' % (cmd, err)
        if stderr: msg += 'See logfile %s for details' % stderr
        raise Exception(msg)

    
def header(s):
    dashes = '-'*len(s)
    print
    print dashes
    print s
    print dashes
    
def open_log(s, mode='r'):
    """Open file as normally, but log those that are being written to
    It is assumed that this file gets cleared out by the script using 
    this function
    """

    fid = open(s, mode)
    
    if mode in ['w', 'a']:
        filenames_updated[s] = 1
    
    return fid

    
def makedir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
        - changes to newly created dir

    Based on            
    http://code.activestate.com/recipes/82465/
    
    Note os.makedirs does not silently pass if directory exists.
    """
    
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        msg = 'a file with the same name as the desired ' \
            'dir, "%s", already exists.' % newdir
        raise OSError(msg)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            makedir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

    os.chdir(newdir)

def replace_string_in_file(filename, s1, s2):
    """Replace string s1 with string s2 in filename 
    """

    # Read data from filename
    infile = open(filename)
    lines = infile.readlines()
    infile.close()

    # Replace and store updated versions
    outfile = open(filename, 'w')
    for s in lines:
        new_string = s.replace(s1, s2).rstrip()

        if new_string.strip() != s.strip():
            print 'Replaced %s with %s' % (s, new_string)
        
        outfile.write(new_string + '\n')
    outfile.close()

    
def get_shell():
    """Get shell if UNIX platform
    Otherwise return None
    """
    
    p = Popen('echo $SHELL', shell=True,
              stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
              
    shell = None
    if p.stdout is not None:
        shell = p.stdout.read().strip()
        shell = os.path.split(shell)[-1] # Only last part of path
        
    return shell

    
            
def set_bash_variable(envvar, envvalue):
    """Modify ~/.bashrc with specified environment variable
    If already exist, append using :
    
    """
    
    fid = open(os.path.expanduser('~/.bashrc'))
    lines = fid.readlines()
    fid.close()
    
    fid = open(os.path.expanduser('~/.bashrc'), 'w')
    found = False
    for line in lines:
        patchedline = line
        
        if envvar in line:
            if line.startswith('export %s=' % envvar):
                # Found - now append
                found = True
                path = line.split('=')[1].strip()
                path += ':' + envvalue
                patchedline = 'export %s=%s  %s\n' % (envvar, path, update_marker)                

        fid.write(patchedline)
        
    fid.write('\n') # In case last line did not have a newline            
                
    if not found:
        # Not found - just add it
        patchedline = 'export %s=%s  %s\n' % (envvar, envvalue, update_marker)
        fid.write(patchedline)
                

    fid.close()

    
