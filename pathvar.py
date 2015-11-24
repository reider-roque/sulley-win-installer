import argparse
import ctypes
import os
import os.path
import sys
import time
import _winreg

if os.name != "nt":
    print("[!] This program is intended to be run on Windows only.")
    sys.exit(1)


def is_dir_path(path):
    # The command line should expand %vars% automatically, but just in case...
    path = os.path.expandvars(path)

    if not os.path.exists(path):
        raise argparse.ArgumentTypeError("Specified path does not exist.")
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError("Specified path is not a directory.")

    # All checks passed, return normalized path
    return os.path.normpath(path);


def is_dir_path_or_index(path_or_index):
    try:
        return int(path_or_index)
    except:
        path_or_index = os.path.expandvars(path_or_index)
        if not os.path.exists(path_or_index) or not os.path.isdir(path_or_index):
            raise argparse.ArgumentTypeError("Specified parameter is not a "
                "valid index or directory path.")

    return os.path.normpath(path_or_index)


_index_was_checked = False
def is_index_and_path(index_or_path):
    global _index_was_checked
    # First parameter is index, check it's validity and set the helper flag
    if not _index_was_checked:
        try:
            index_or_path = int(index_or_path)
            _index_was_checked = True
        except:
            raise argparse.ArgumentTypeError("Specified index is not a valid integer.")
    # If index checking flag is set the we deal with second parameter which is path
    else:
        # Leverage is_dir_path to check if the second argument is correct    
        index_or_path = is_dir_path(index_or_path)
        _index_was_checked = False

    return index_or_path


def open_path_var_key(mode):
    hKey = None

    if mode == "system":
        hKey = _winreg.OpenKey(
            _winreg.HKEY_LOCAL_MACHINE,
            r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
            0, 
            _winreg.KEY_READ | _winreg.KEY_SET_VALUE)
    elif mode == "user":
        hKey = _winreg.OpenKey(
            _winreg.HKEY_CURRENT_USER,
            r'Environment',
            0, 
            _winreg.KEY_READ | _winreg.KEY_SET_VALUE)

    return hKey


def get_reg_value(mode):
    hKey = open_path_var_key(mode)
    try:
        reg_value, _ = _winreg.QueryValueEx(hKey, "PATH")
    except WindowsError as e:
        if e.errno == 2: # The system cannot find the file specified
            # Create the value if it does not exist
            reg_value = ""
            _winreg.SetValueEx(hKey, "PATH", 0, _winreg.REG_EXPAND_SZ, reg_value)
            _winreg.FlushKey(hKey)

    hKey.Close()

    return reg_value


def get_path_var(mode):
    if mode != "both":
        reg_value = get_reg_value(mode)
        paths = reg_value.rstrip(';').split(';')
    else:
        reg_value = get_reg_value("system")
        paths = reg_value.rstrip(';').split(';')

        reg_value = get_reg_value("user")
        paths = paths + reg_value.rstrip(';').split(';')

    # Remove all empty strings from paths
    while "" in paths: paths.remove("")
    
    return paths


def set_path_var(mode, paths):
    reg_value = ";".join(paths)
    hKey = open_path_var_key(mode)
    _winreg.SetValueEx(hKey, "PATH", 0, _winreg.REG_EXPAND_SZ, reg_value)
    _winreg.FlushKey(hKey)
    hKey.Close()

    # Notify system of PATH change. Use SendMessageTimeout instead of
    # SendMessage because with Python 3 it hangs awaiting for response
    # that never comes
    SendMessageTimeout = ctypes.windll.user32.SendMessageTimeoutW
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    SMTO_ABORTIFHUNG = 0x2
    SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, u'Environment',
        SMTO_ABORTIFHUNG, 500)


def normalize_paths(paths):
    norm_paths = [os.path.normpath(os.path.expandvars(entry)) 
                  for entry in paths]
    return norm_paths


def print_path_var(mode, normalized=True):
    paths = get_path_var(mode)

    if normalized:
        paths = normalize_paths(paths)
    
    if not paths:
        print("\n[*] {} PATH variable is empty.".format(mode.capitalize()))
        return

    i = 0
    print ""
    for path in paths:
        print("{0:02d} {1}".format(i, path))
        i += 1

def filter_dup_paths(paths, norm_paths):
    filtered_norm_paths = []
    filtered_paths = []
    for i in range(0, len(norm_paths)):
        if norm_paths[i].lower() not in filtered_norm_paths:
            filtered_norm_paths.append(norm_paths[i].lower())
            filtered_paths.append(paths[i])

    return filtered_paths


def cross_filter_dup_paths(user_paths, norm_user_paths, norm_system_paths):
    norm_system_paths = [path.lower() for path in norm_system_paths]
    filtered_norm_user_paths = []
    for i in range(0, len(norm_user_paths)):
        if norm_user_paths[i].lower() not in norm_system_paths:
            filtered_norm_user_paths.append(user_paths[i])

    return filtered_norm_user_paths


def remove_invalid_paths(mode, paths):
    valid_paths = []
    invalid_paths = []
    for path in paths:
        exp_path = os.path.expandvars(path)
        if os.path.exists(exp_path) and os.path.isdir(exp_path):
            valid_paths.append(path)
        else:
            invalid_paths.append(path)

    # Print invalid paths if there were any
    if invalid_paths:
        i = 0
        print "\n[+] The following invalid paths were removed from {} PATH:\n".format(mode)
        for path in invalid_paths:
            print("{0:02d} {1}".format(i, path))
            i += 1
        print("\n--------------------")

    return valid_paths


# For customizing error output
class ArgumentParser(argparse.ArgumentParser):
    def error(self, msg):
        sys.stderr.write('Error: {}\n'.format(msg))
        self.print_help()
        sys.exit(2)


# For capitalizing of certian words in help output
argparse._ = lambda s: {"usage: ": "Usage: ", "optional arguments": "Optional arguments", 
    "show this help message and exit": "Show this help message and exit"}.get(s, s)

parser = ArgumentParser(description="Modify user or system PATH variable.",
    usage="%(prog)s OPTIONS [PATH|INDEX]",
    epilog="Written by Oleg Mitrofanov (http://www.wryway.com/) (c) 2015. "
    "Inspired by Gerson Kurz's pathed tool (http://p-and-q.com).")

mode_group = parser.add_mutually_exclusive_group()
mode_group.add_argument("-u", "--user", help="Operate on current user PATH variable",
    action="store_true")
mode_group.add_argument("-s", "--system", help="Operate on system PATH variable",
    action="store_true")
mode_operation = parser.add_mutually_exclusive_group(required=True)
mode_operation.add_argument("-a", "--append", help="Append directory path to "
    "PATH variable", metavar="PATH", type=is_dir_path)
mode_operation.add_argument("-p", "--prepend", help="Prepend directory path to "
    "PATH variable", metavar="PATH", type=is_dir_path)
mode_operation.add_argument("-i", "--insert", help="Insert directory path to "
    "PATH variable at the specified position", nargs=2, metavar=("INDEX", "PATH"),
    type=is_index_and_path)
mode_operation.add_argument("-r", "--remove", help="Remove directory path from "
    "PATH variable. Path to remove can be specified either by index, or by the "
    "actual directory path string", metavar="PATH|INDEX", type=is_dir_path_or_index)
mode_operation.add_argument("-l", "--list", help="List all directory paths for "
    "the user, system, or, if non specified, both PATHs combined", 
    action="store_true")
mode_operation.add_argument("-t", "--trim", help="Trim duplicates from system, "
    "user, or, if none specified, both PATHs combined", action="store_true")
args = parser.parse_args()

mode = None
path = None
index = None

if args.user:
    mode = "user"
elif args.system:
    mode = "system"

if not args.append is None:
    operation = "append"
    path = unicode(args.append, "utf-8")
elif not args.prepend is None:
    operation = "prepend"
    path = unicode(args.prepend, "utf-8")
elif not args.insert is None:
    operation = "insert"
    index = args.insert[0]
    path = unicode(args.insert[1], "utf-8")
elif not args.remove is None:
    operation = "remove"
    if isinstance(args.remove, int):
        index = args.remove
    elif isinstance(args.remove, str):
        path = unicode(args.remove, "utf-8")
# args.list and args.trim are boolean, can't test for None, should
# test for boolean
elif args.list:
    operation = "list"
elif args.trim:
    operation = "trim"

# If mode is not explicitly set with --user or --system flags,
# the list and trim will operate on combined list, while all
# other operations will act on system path
if mode is None:
    if operation == "list" or operation == "trim":
        mode = "both"
    else:
        mode = "system"

paths = get_path_var(mode)
# Normalize paths by expanding all %vars%
norm_paths = normalize_paths(paths)

if operation == "append":
    # Check against norm_paths, but append to paths so that the original
    # String is not modified.
    if path in norm_paths:
        print_path_var(mode)
        print("\n[!] '{}' is already in the {} PATH. Nothing to do.".format(path, mode))
    else:
        paths.append(path)
        set_path_var(mode, paths)
        print_path_var(mode)
        print("\n[+] '{}' was appended to {} PATH.".format(path, mode))
        print("[*] To reflect the change in command prompts they must be restarted.")

elif operation == "prepend":
    if path in norm_paths:
        print_path_var(mode)
        print("\n[!] '{}' is already in the {} PATH. Nothing to do.".format(path, mode))
    else:
        paths.insert(0, path)
        set_path_var(mode, paths)
        print_path_var(mode)
        print("\n[+] '{}' was prepended to {} PATH.".format(path, mode))
        print("[*] To reflect the change in command prompts they must be restarted.")

elif operation == "insert":
    if path in norm_paths:
        print_path_var(mode)
        print("\n[!] '{}' is already in the {} PATH. Nothing to do.".format(path, mode))
    else:
        # No need to worry if index is out of bounds, the insert operatin handles it
        paths.insert(index, path)
        set_path_var(mode, paths)
        print_path_var(mode)
        print("\n[+] '{}' was inserted into position {} of {} PATH.".format(path, 
            index, mode))
        print("[*] To reflect the change in command prompts they must be restarted.")

elif operation == "remove":
    if path:
        if path in paths:
            paths.remove(path)
            set_path_var(mode, paths)
            print_path_var(mode)
            print("\n[+] '{}' was removed from {} PATH.".format(path, mode))
            print("[*] To reflect the change in command prompts they must be restarted.")
        else:
            print("\n[!] '{}' is not in {} PATH. Nothing to do.".format(path, mode))
    elif index is not None:
        if index < 0 or index > len(paths)-1:
            print_path_var(mode)
            print("\n[!] Index {} is out of bounds. Nothing to do.".format(index))
        else:
            path_to_remove = paths[index]
            del paths[index]
            set_path_var(mode, paths)
            print_path_var(mode)
            print("\n[+] '{}' was removed from {} PATH.".format(path_to_remove, mode))
            print("[*] To reflect the change in command prompts they must be restarted.")

elif operation == "list":
    print_path_var(mode)

elif operation == "trim":
    if mode != "both":
        paths = remove_invalid_paths(mode, paths)
        # Need to re-run it since paths may have changed
        norm_paths = normalize_paths(paths)
        paths = filter_dup_paths(paths, norm_paths)
        set_path_var(mode, paths)
        print_path_var(mode)
        print("\n[+] {} PATH was cleaned of invalid and duplicate "
            "directory paths.".format(mode.capitalize()))
        print("[*] To reflect the change in command prompts they must be restarted.")
    else:
        user_paths = get_path_var("user")
        user_paths = remove_invalid_paths("user", user_paths)
        norm_user_paths = normalize_paths(user_paths)
        user_paths = filter_dup_paths(user_paths, norm_user_paths)

        system_paths = get_path_var("system")
        system_paths = remove_invalid_paths("system", system_paths)
        norm_system_paths = normalize_paths(system_paths)
        system_paths = filter_dup_paths(system_paths, norm_system_paths)

        user_paths = cross_filter_dup_paths(user_paths, norm_user_paths, norm_system_paths)
        
        set_path_var("user", user_paths)
        set_path_var("system", system_paths)
        print_path_var(mode)
        print("\n[+] Sysem and user PATHs were cleaned of invalid and duplicate "
            "directory paths.")
        print("[*] To reflect the change in command prompts they must be restarted.")