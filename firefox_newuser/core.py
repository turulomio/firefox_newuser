from argparse import ArgumentParser, RawTextHelpFormatter, SUPPRESS
from colorama import init, Style
from firefox_newuser import __versiondate__, __version__, add_user_securely
from firefox_newuser.commons import detect_condition, detect_command, string_ok, string_fail, argparse_epilog, _
from getpass import getuser
from glob import glob
from os import path, makedirs, system, environ, getuid
from psutil import process_iter
from secrets import token_urlsafe
from subprocess import run, PIPE, STDOUT
import pwd
from shutil import move
from sys import stdout
from tqdm import tqdm



def main():
    init()
    parser=ArgumentParser(description=_('Script to execute a firefox instance with a recently created user from wayland. It deletes user after firefox execution'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--sync', help=_("Directory to sync files to after closing firefox"), default="/root")
    parser.add_argument('--host-uid', type=int, help=SUPPRESS)
    args=parser.parse_args()
    
    if getuser()=="root":
        fn_password = token_urlsafe(32)
        add_user_securely("firefox_newuser", fn_password)
        print(_("Adding user 'firefox_newuser' with password '{0}' ...").format(fn_password))

        run("chown -Rvc firefox_newuser:users /home/firefox_newuser", shell=True, capture_output=True)
        print(_("Changing permissions to /home/firefox_newuser..."))

        # Sound support: share the host user's PulseAudio/PipeWire socket
        pulse_env = ""
        if args.host_uid:
            host_runtime_dir = f"/run/user/{args.host_uid}"
            try:
                host_home = pwd.getpwuid(args.host_uid).pw_dir
            except KeyError:
                host_home = None

            pulse_socket = f"{host_runtime_dir}/pulse/native"
            pw_socket = f"{host_runtime_dir}/pipewire-0"
            
            # Grant the new user access to the host's runtime directory
            run(f"setfacl -m u:firefox_newuser:x {host_runtime_dir}", shell=True, capture_output=True)
            
            if path.exists(pulse_socket):
                run(f"setfacl -m u:firefox_newuser:x {path.dirname(pulse_socket)}", shell=True, capture_output=True)
                run(f"setfacl -m u:firefox_newuser:rw {pulse_socket}", shell=True, capture_output=True)
                pulse_env += f"PULSE_SERVER=unix:{pulse_socket} "
            
            if path.exists(pw_socket):
                run(f"setfacl -m u:firefox_newuser:rw {pw_socket}", shell=True, capture_output=True)
                # For native PipeWire support, point to the host's runtime directory
                pulse_env += f"PIPEWIRE_RUNTIME_DIR={host_runtime_dir} PIPEWIRE_REMOTE=pipewire-0 "
            
            # PulseAudio/PipeWire Cookie authentication
            possible_cookies = [
                path.join(host_home, ".config/pulse/cookie") if host_home else None,
                f"{host_runtime_dir}/pulse/cookie"
            ]
            for cookie_path in filter(None, possible_cookies):
                if path.exists(cookie_path):
                    run(f"setfacl -m u:firefox_newuser:r {cookie_path}", shell=True, capture_output=True)
                    pulse_env += f"PULSE_COOKIE={cookie_path} "
                    break

        firefox_cmd = f"env {pulse_env}firefox --private-window www.google.com"

        #Launching firefox
        b=run(f"kdesu -u firefox_newuser -c '{firefox_cmd}'", shell=True, capture_output=True)
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
        system(f"""su - -c "{environ["_"]} --sync '{args.sync}' --host-uid {getuid()}" """) #Launches same program again as root
