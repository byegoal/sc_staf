import subprocess
import time

def get_time(time_format, given_time=None):

    if time_format == 1:
        ISOTIMEFORMAT="%Y-%m-%d %H:%M:%S"
    elif time_format == 2:
        ISOTIMEFORMAT="%Y-%m-%d-%H-%M-%S"

    if given_time:
        return time.strftime(ISOTIMEFORMAT, time.localtime(given_time))
    else:
        start_time = time.time()
        #print "start time:" + time.strftime(ISOTIMEFORMAT, time.localtime(start_time))
        return time.strftime(ISOTIMEFORMAT, time.localtime(start_time))
    
def call_cmd(command, log_file, action):

    start_time = time.time()
    log_file.write("START - " + action + " : " + get_time(1, start_time) + "\r\n")

    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = proc.communicate()

    #if has_error:
    if stderr_value:
        print stderr_value
        log_file.write(stderr_value + "\r\n")

    if stdout_value:
        print stdout_value
        log_file.write(stdout_value + "\r\n")
     
    end_time = time.time()
    spent_time = end_time - start_time

    log_file.write("End - " + action + " : " + get_time(1, end_time) + "\r\n")
    log_file.write("Time Taken:" + str(spent_time) + "\r\n")


work_path = "C:\\STAF\\lib\\python\\secureCloud\\managementAPI\\"
log_file_path = work_path + "python_git_sync.log"
log_file = open(log_file_path, "w")

call_cmd(work_path + "git_sync.exe", log_file, "running auto-it git_sync.exe")


log_file.close()