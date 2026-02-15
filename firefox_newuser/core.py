from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import init, Style
from firefox_newuser import __versiondate__, __version__, add_user_securely
from firefox_newuser.commons import detect_condition, detect_command, string_ok, string_fail, argparse_epilog, _
from getpass import getuser
from glob import glob
from os import path, makedirs, system, environ
from psutil import process_iter
from secrets import token_urlsafe
from subprocess import run, PIPE, STDOUT
from shutil import move
from sys import stdout
from tqdm import tqdm



def main():
    init()
    parser=ArgumentParser(description=_('Script to execute a firefox instance with a recently created user from wayland. It deletes user after firefox execution'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--sync', help=_("Directory to sync files to after closing firefox"), default="/root")
    args=parser.parse_args()
    
    if getuser()=="root":
        fn_password = token_urlsafe(32)
        add_user_securely("firefox_newuser", fn_password)
        print(_("Adding user 'firefox_newuser' with password '{0}' ...").format(fn_password))


        run("chown -Rvc firefox_newuser:users /home/firefox_newuser", shell=True, capture_output=True)
        print(_("Changing permissions to /home/firefox_newuser..."))

        #Launching firefox
        b=run("kdesu -u firefox_newuser -c 'firefox --private-window www.google.com'", shell=True, capture_output=True)
        print(b)
        print(_("Launching firefox..."))

        #Killing firefox
        run("su - firefox_newuser -c 'fusermount -u /home/firefox_newuser/.cache/doc'", shell=True, capture_output=True)
        run("pkill -9 -U firefox_newuser", shell=True, capture_output=True)
        
        detect_command(
            "userdel firefox_newuser", 
            _("Deleting user 'firefox_newuser'...")
        )
        
        sync_files=[]
        for filename in glob('/home/firefox_newuser/**', recursive=True):
            if path.isfile(filename):
                sync_files.append(filename)
        
        if len(sync_files)>0:
            makedirs(args.sync, exist_ok=True)
            for filename in tqdm(sync_files, desc=Style.BRIGHT +_("Moving {0} files to '{1}'").format(len(sync_files), args.sync)+ Style.RESET_ALL):
                move(filename, path.join(args.sync, path.basename(filename)))
            
            stdout.write(Style.BRIGHT + _("Checking {0} files have been moved to '{1}'...").format(len(sync_files), args.sync) + Style.RESET_ALL+" ")
            errors=0
            for filename in sync_files:
                if not path.exists(path.join(args.sync, path.basename(filename))):
                    errors=errors+1
            if errors==0:
                print(string_ok())
            else:
                print(string_fail())

        
        run("rm -Rf /home/firefox_newuser", shell=True, capture_output=True)
                
        detect_condition(
            not path.exists("/home/firefox_newuser/"), 
            "Checking directory '/home/firefox_newuser' is deleted..."
        )
        
        process_list = [proc.pid for proc in process_iter() if proc.username() == "firefox_newuser"]
        detect_condition(
            len(process_list)==0, 
            "Checking there aren't firefox_newuser process..."
        )
        
  
    else:
        print(_("Introduce root password to launch firefox_newuser"))
        system(f"""su - -c "{environ["_"]} --sync '{args.sync}'" """) #Launches same program again as root
