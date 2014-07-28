import os.path
import fnmatch
import shutil


def search_file(search_filename, search_path):
        for root, dirnames, filenames in os.walk(search_path):
                for filename in fnmatch.filter(filenames, search_filename):
                        return os.path.join(root, filename)
        return None


def move_tmstaf_log(REMOTE_MACHINE, REMOTE_FILEPATH, log_name):
    source_path = search_file(log_name, REMOTE_FILEPATH)
    dist_path = os.path.join(REMOTE_FILEPATH + log_name)
    shutil.copyfile(source_path, dist_path)


def wait_agent_stop(intTimeout):
    for i in range(intTimeout):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        procNames = []
        for pid in pids:
            procNames.append(open(os.path.join(
                                  '/proc', pid, 'cmdline'), 'rb').read())
        if " ".join(procNames).find("scagent") == -1:
            return 1
    return 0
