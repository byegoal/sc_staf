"""
define error code
Please use "Error" + $filename as class name, then define error code
"""


class ErrorautoServerMain():
    """
    The code for auto server main
    """
    SUCCESS = 0
    FAIL = 1
    STOP = 2
    INI_SETTING_ERROR = 3
    FOLDER_NOT_EXIST = 4
    DOWNLOAD_BUILD_FAIL = 5
    STAF_QUIT_FAIL = 6
    STAF_READY_FAIL = 7
    STATIC_CHECK_FAIL = 8
    TASK_FILE_NONE = 9
    NO_TARGET_MACHINES = 10
    SIA_DOWNLOAD_URL_FAIL = 11
    FOLDER_EXIST = 12


class ErrorWin32ui():
    HANDLE_NOT_FIND = 0
    SUCCESS = 0
    FAIL = 1
