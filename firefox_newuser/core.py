from argparse import ArgumentParser, RawTextHelpFormatter
from colorama import init, Fore, Style
from firefox_newuser.__init__ import __versiondate__, __version__
from getpass import getuser
from gettext import translation
from glob import glob
from importlib.resources import files
from os import path, makedirs, system
from psutil import process_iter
from shutil import move
from subprocess import run, PIPE, STDOUT
from sys import stdout
from tqdm import tqdm

try:    
    t=translation('firefox_newuser', files("firefox_newuser") / 'locale')
    _=t.gettext
except:
    _=str
    
    
class Answer:
    def __init__(self, success, comments=[]):
        self.success=success
        self.comments=comments

    def print(self):
        if self.success:
            print(" "+ string_ok())
        else:
            print(" "+ string_fail())
            for line in self.comments:
                print("   - "+ line)
            
def string_ok():
        return Style.BRIGHT + "[" + Fore.GREEN+_("OK") + Fore.WHITE + "]" + Style.RESET_ALL
        
def string_fail():
        return Style.BRIGHT + "[" + Fore.RED+_("FAILED") + Fore.WHITE + "]" + Style.RESET_ALL

## Function used in argparse_epilog
## @return String
def argparse_epilog():
    return _("Developed by Mariano Muñoz 2020-{}").format(__versiondate__.year)
    
## @param condition is a boolean expresion
def detect_condition(condition,  title, additional_fail_comments=[]):
    print(Style.BRIGHT + title + Style.RESET_ALL , end="")
    if condition==True:
        ans= Answer(True)
    else:
        ans= Answer(False, additional_fail_comments)
    ans.print()
    return ans.success

def detect_command(command,  title=None, additional_fail_comments=[]):
    if title is None:
        title=command
    print(Style.BRIGHT + title + Style.RESET_ALL , end="")
    
    p=run(command, shell=True, stdout=PIPE, stderr=STDOUT)
    if p.returncode==0:
        ans= Answer(True)
    else:
        comments=[_("Command '{0}' exited with code {1}").format(command, p.returncode)]
        comments.append(p.stdout.decode("UTF-8"))
        comments=comments+additional_fail_comments
        ans= Answer(False, comments)
    ans.print()
    return ans.success

def detect_file(file):
    print(Style.BRIGHT + _("Detecting file '{0}'...").format(file) + Style.RESET_ALL , end="")
    if path.exists(file):
        ans= Answer(True)
    else:
        ans=Answer(False, [_("File '{0}' doesn't exist").format(file)])
    ans.print()
    return ans.success
    
    
def detect_file_contents(file, content, additional_fail_comments):
    stdout.write(Style.BRIGHT + _("Detecting file content in '{0}'...").format(file) + Style.RESET_ALL )
    stdout.flush()
    if path.exists(file):
        with open(file, "r") as f:
            found=False
            for line in f.readlines():
                if content in line:
                    found=True
                    
        if found==True:
            ans=Answer(True)
        else:
            comments= [_("'{0}' wasn't found in '{1}'").format(content, file)]+ additional_fail_comments
            ans=Answer(False, comments)
    else:
        ans=Answer(False, [_("File '{0}' doesn't exist").format(file)])
    ans.print()
    return ans.success

def main():
    init()
    parser=ArgumentParser(description=_('Script to execute a firefox instance with a recently created user. It deletes user after firefox execution'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--sync', help=_("Directory to sync files to after closing firefox"), default="/root")
    args=parser.parse_args()
    
    if getuser()=="root":
        detect_file_contents(
            "/etc/pulse/default.pa", 
            "load-module module-native-protocol-unix auth-anonymous=1 socket=/tmp/my-pulse-socket-name", 
            [
                _("You need to set it up exactly in order to have sound enabled"), 
            ]
        )
        detect_command(
            "useradd firefox_newuser -g users -G audio,video", 
            _("Adding user 'firefox_newuser'...")
        )
        makedirs("/home/firefox_newuser/.pulse/", exist_ok=True)
        with open("/home/firefox_newuser/.pulse/client.conf", "w") as f:
            f.write("default-server = unix:/tmp/my-pulse-socket-name")
        run("chown -Rvc firefox_newuser:users /home/firefox_newuser", shell=True, capture_output=True)
        #Launching firefox
        run("su - firefox_newuser -c 'DISPLAY=:0 firefox --private-window www.google.com'", shell=True, capture_output=True)

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
        run("xhost +", shell=True, capture_output=True)
        print(_("Introduce root password to launch firefox_newuser"))
        system(f"""su - -c "firefox_newuser --sync '{args.sync}'" """)


