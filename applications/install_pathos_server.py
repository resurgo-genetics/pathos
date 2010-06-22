#!/usr/bin/env python
"""
remote bash-script install of given package
"""

from pathos.core import copy,run
from pathos.hosts import get_profile, register_profiles


if __name__ == '__main__':

##### CONFIGURATION & INPUT ########################
  # set the default remote host
 #rhost = 'localhost'
  rhost = 'upgrayedd.danse.us'
 #rhost = 'shc-b.cacr.caltech.edu'
 #rhost = 'login.cacr.caltech.edu'

  from time import sleep
  delay = 0.0
  big_delay = 5.0

  # set the default package & version
  package = 'pp'    #XXX: package name MUST correspond to X in installer-X.sh
  version = '1.5.7' #XXX: also hardwired in installer-X.sh

  print """Usage: python install_package.py [package] [version] [hostname] 
    [package] - name of the package to install
    [version] - version of the package to install
    [hostname] - name of the host on which to install the package
    defaults are: "%s" "%s" "%s".""" % (package, version, rhost)

  # get package to install from user
  import sys
  try:
    myinp = sys.argv[1],sys.argv[2]
  except: myinp = None
  if myinp:
    package,version = myinp #XXX: should test validity here... (filename)
  else: pass # use default
  del myinp

  # get remote hostname from user
  import sys
  try:
    myinp = sys.argv[3]
  except: myinp = None
  if myinp:
    rhost = myinp #XXX: should test rhost validity here... (how ?)
  else: pass # use default
  del myinp

  # my remote environment (should be auto-detected)
  profiles = {'upgrayedd.danse.us':'.profile',
              'login.cacr.caltech.edu':'.cshrc'}
  register_profiles(profiles)
  profile = get_profile(rhost)

##### CONFIGURATION & INPUT ########################

  file = 'install-%s-%s.sh' % (package,version)
  # XXX: should use easy_install, if is installed...

  import tempfile
# tempfile.tempdir = "~" #XXX: uncomment if cannot install to '/tmp'
  dest = tempfile.mktemp()+"_install" #XXX: checks local (not remote)

  # check for existing installation
  command = "source %s; python -c 'import %s'" % (profile,package)
  print 'executing {ssh %s "%s"}' % (rhost,command)
  error = run(command,rhost)
  if error in ['', None]:
    print '%s is already installed on %s' % (package,rhost)
# elif error[:39] == 'This system is available for legitimate use'[:39] \
#      and rhost[:3] == 'shc-b.cacr.caltech.edu'[:3]:
##     and error[-35:-1] == 'an authorized user of this system.'[-35:] \
#   print '%s is already installed on %s' % (package,rhost)
    #XXX: could parse 'error' for "ImportError" ==> not installed
    #XXX: could use command="python -c 'import X; X.__version__'"
    #XXX  ...returns version# or "AttributeError" ==> non-standard version tag
  else:
    print error
    sleep(delay)

    # create install directory
    command = 'mkdir -p %s' % dest #FIXME: *nix only
    print 'executing {ssh %s "%s"}' % (rhost,command)
    report = run(command,rhost)
    #XXX: could check for clean install by parsing for "Error" (?)
    sleep(delay)

    # copy over the installer to remote host
    print 'executing {scp %s %s:%s}' % (file,rhost,dest)
    copy(file,rhost,dest)
    sleep(delay)

    # run the installer
    command = 'cd %s; ./%s' % (dest,file) #FIXME: *nix only
    print 'executing {ssh %s "%s"}' % (rhost,command)
    report = run(command,rhost)
    #XXX: could check for clean install by parsing for "Error" (?)
    sleep(big_delay)

    # remove remote install file
#   killme = dest+'/'+file  #FIXME: *nix only
#   command = 'rm -f %s' % killme #FIXME: *nix only
#   print 'executing {ssh %s "%s"}' % (rhost,command)
#   run(command,rhost)

    # remove remote package unpacking directory
#   killme = dest+'/'+package+'-'+version #FIXME: dies for NON-STANDARD naming
#   command = 'rm -rf %s' % killme #FIXME: *nix only
#   print 'executing {ssh %s "%s"}' % (rhost,command)
#   run(command,rhost)

    # remove remote install directory
    killme = dest
    command = 'rm -rf %s' % killme #FIXME: *nix only
    print 'executing {ssh %s "%s"}' % (rhost,command)
    run(command,rhost)

    # check installation
    command = "source %s; python -c 'import %s'" % (profile,package)
    print 'executing {ssh %s "%s"}' % (rhost,command)
    error = run(command,rhost)
    if error in ['', None]:
      pass # is installed
    else:
      print error
#     raise ImportError, "failure to install package"
