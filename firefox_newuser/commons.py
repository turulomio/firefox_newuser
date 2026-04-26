from datetime import datetime
from subprocess import run
from colorama import init, Fore, Style
from gettext import translation
from importlib.resources import files
from subprocess import run, PIPE, STDOUT, CompletedProcess
from sys import stdout, exit as sys_exit # Renamed exit to avoid conflict with path.exists
from getpass import getuser # Added for ensure_root_privileges
from os import system, environ, getuid # Added for ensure_root_privileges

from os import path # Added for path.exists in detect_file and detect_file_contents
import pwd # Added for launch_command_as_user_with_sound
from typing import Optional # Added for type hinting in launch_command_as_user_with_sound

__version__= '1.0.0'
__versiondatetime__=datetime(2026, 2, 15, 11, 5)
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


def launch_command_as_user_with_sound(
    username: str,
    command: str,
    host_uid: Optional[int] = None,
    capture_output: bool = True,
    shell: bool = True
) -> CompletedProcess:
    """
    Launches a command as a specified user, with environment variables set up
    for PipeWire/PulseAudio sound support, typically using kdesu.

     This function is expected to be run with root privileges, as it uses
     'setfacl' and 'kdesu', which require elevated permissions to manage
     user permissions and switch users effectively.
    
    Args:
        username (str): The user to run the command as.
        command (str): The command string to execute.
        host_uid (Optional[int]): The UID of the host user, required for sound bridging.
                                  If None, sound bridging will not be attempted.
        capture_output (bool): Whether to capture stdout and stderr.
        shell (bool): Whether to execute the command through the shell.

    Returns:
        subprocess.CompletedProcess: The result of the run command.
    """
    pulse_env = ""
    if host_uid is not None:
        # 1. Locate the host's runtime directory (where communication sockets live)
        host_runtime_dir = f"/run/user/{host_uid}"
        try:
            host_home = pwd.getpwuid(host_uid).pw_dir
        except KeyError:
            host_home = None

        # 2. Define paths for the communication sockets
        pulse_socket = f"{host_runtime_dir}/pulse/native"
        pw_socket = f"{host_runtime_dir}/pipewire-0"
        
        # 3. Permissions (ACLs):
        # We use 'setfacl' to grant the temporary user 'x' (search/execute) permission 
        # on the host's runtime directory. Without this, the new user cannot "enter" 
        # the directory to see the sockets, even if they have permission for the sockets themselves.
        run(f"setfacl -m u:{username}:x {host_runtime_dir}", shell=True, capture_output=True)
        
        if path.exists(pulse_socket):
            # Grant access to the pulse subdirectory and the socket itself
            run(f"setfacl -m u:{username}:x {path.dirname(pulse_socket)}", shell=True, capture_output=True)
            run(f"setfacl -m u:{username}:rw {pulse_socket}", shell=True, capture_output=True)
            # Tell Firefox to use this specific Unix socket for PulseAudio
            pulse_env += f"PULSE_SERVER=unix:{pulse_socket} "
        
        if path.exists(pw_socket):
            # Grant read/write access to the native PipeWire socket
            run(f"setfacl -m u:{username}:rw {pw_socket}", shell=True, capture_output=True)
            # Tell PipeWire clients where to find the host's server
            pulse_env += f"PIPEWIRE_RUNTIME_DIR={host_runtime_dir} PIPEWIRE_REMOTE=pipewire-0 "
        
        # 4. The Cookie (Authentication):
        possible_cookies = [
            path.join(host_home, ".config/pulse/cookie") if host_home else None,
            f"{host_runtime_dir}/pulse/cookie"
        ]
        for cookie_path in filter(None, possible_cookies):
            if path.exists(cookie_path):
                run(f"setfacl -m u:{username}:r {cookie_path}", shell=True, capture_output=True)
                pulse_env += f"PULSE_COOKIE={cookie_path} "
                break
    
    full_command_with_env = f"env {pulse_env}{command}"
    return run(f"kdesu -u {username} -c '{full_command_with_env}'", shell=shell, capture_output=capture_output)
    
    
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
