from datetime import datetime
from subprocess import run
from colorama import init, Fore, Style
from gettext import translation
from importlib.resources import files
from subprocess import run, PIPE, STDOUT
from sys import stdout

__version__= '0.10.0dev'
__versiondatetime__=datetime(2026, 2, 15, 9, 55)
__versiondate__=__versiondatetime__.date()

def add_user_securely(username, password):
    # Create the user first without a password
    run(f"useradd -m {username}", shell=True, check=True)
    
    # Use chpasswd to set the password (it takes "user:pass" via stdin)
    input_str = f"{username}:{password}"
    run('chpasswd', input=input_str.encode(), shell=True, check=True)
    print(f"User {username} updated.")

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