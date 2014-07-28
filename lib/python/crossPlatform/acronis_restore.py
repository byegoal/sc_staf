from trend import win32ui
from trend.error_code import ErrorWin32ui
import trend.winProcessUtil
from time import sleep
import trend.winVerUtil
import thread


def click_btn(class_list, handler_instance_dict={}, action='Left_Click', xpos=0, ypos=0, time_out_ts=10, btn_click=1):
    """
        B{Click button function for this module use only not public.}
        @type class_list: List
        @param class_list: A list of window class name for findwindow use
        @type handler_instance_dict: Dictionary
        @param handler_instance_dict: Index for correct class. Acronis will has a lot of redundant class name, so
                                      you have to provide the index if there has same child class name.
                                      Ex. if there has 3 child class name FXVerticalFrame under ATIShellWelcomeGeneralPage
                                          and ATIShellWelcomeGeneralPage is the 3rd child, and the target child is 2nd FXVerticalFrame
                                          so you have to specify list with {3:2}
        @type action: String
        @param action: Left_Click
        @type xpos: Integer
        @param xpos: X axis for UI component
        @type ypos: Integer
        @param ypos: Y axis for UI component
        @type time_out_ts: Integer
        @param time_out_ts: Time out value
        @type btn_click: Integer
        @param btn_click: 1 = Clieck Button (Default)
                          others = return success if found handler
    """
    cnt = 0
    handler = 0
    target_handler_seq = 999
    for target in class_list:
        if cnt == len(class_list) - 1:
            break
        cnt = cnt + 1
        print cnt, handler, target, class_list[cnt]
        if target == 'Desktop':
            handler = win32ui.findwindow(target, class_list[
                cnt], time_out=time_out_ts, intRecursive=0)
        else:
            if handler != 0:
                if len(handler_instance_dict) != 0:
                    handler_instance_dict.keys().sort()
                    all_target_list = handler_instance_dict.keys()
                    target_handler_seq = int(all_target_list[0])

                if cnt == target_handler_seq:
                    # Because there has N classes under parent handler, so it need traverse to (target_handler_seq)-th in handler for target class
                    int_instance_number = handler_instance_dict.pop(
                        target_handler_seq)
                    handler = win32ui.findwindow_by_class(handler, class_list[cnt], int_instance_number, time_out_ts, intRecursive=0)
                else:
                    handler = win32ui.findwindow(handler, class_list[cnt], time_out=time_out_ts, intRecursive=0)
            else:
                print 'Cannot find handler ' + class_list[
                    cnt] + ' under ' + target + '\n'
                return ErrorWin32ui.HANDLE_NOT_FIND
    print handler
    if handler != 0:
        if btn_click == 1:
            return win32ui.click_button(handler, 0, action, xpos, ypos)
        else:
            return ErrorWin32ui.SUCCESS


def click_btn_recovery_task(x, y, current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame', 'ATIShellWelcomeGeneralPage', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXAShellTaskArea']
        return click_btn(class_seq, {4: 3}, xpos=x, ypos=y)
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'FXATIShellWindow', 'FXVerticalFrame', 'ATIShellWelcomeGeneralPage', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXAShellTaskArea']
        return click_btn(class_seq, {5: 3}, xpos=x, ypos=y)


def click_btn_disk_recovery(x, y, current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame', 'ATIShellBackupRestorePage', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXAShellViewArea', 'FXVerticalFrame', 'FXVerticalFrame']
        return click_btn(class_seq, {4: 3}, xpos=x, ypos=y)
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'FXATIShellWindow', 'FXVerticalFrame', 'ATIShellBackupRestorePage', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXAShellViewArea', 'FXVerticalFrame', 'FXVerticalFrame']
        return click_btn(class_seq, {5: 3}, xpos=x, ypos=y)


def click_btn_archive_next(current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXAStyleButton']
        return click_btn(class_seq, {6: 2})
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'ArchiveWizard', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXAStyleButton']
        return click_btn(class_seq, {7: 2})


def click_btn_archive_cancel(current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXAStyleButton']
        return click_btn(class_seq, {6: 6})
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'ArchiveWizard', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXAStyleButton']
        return click_btn(class_seq, {7: 6})


def select_dest_partition(x, y, current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXAPartitionsRestoreStage', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXADaImagerPartitionList']
        return click_btn(class_seq, {3: 2}, xpos=x, ypos=y)
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'ArchiveWizard', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXAPartitionsRestoreStage', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXADaImagerPartitionList']
        return click_btn(class_seq, {4: 2}, xpos=x, ypos=y)


def click_btn_proceed(current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXAStyleButton']
        return click_btn(class_seq, {6: 4})
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'ArchiveWizard', 'FXVerticalFrame', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXHorizontalFrame', 'FXAStyleButton']
        return click_btn(class_seq, {7: 4})


def pooling_warning_box():
    class_seq = ['Desktop', 'FXAMessageBoxImpl']
    return click_btn(class_seq, time_out_ts=10, btn_click=0)


def pooling_archive_processing(current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame', 'FXHorizontalFrame',
                     'FXVerticalFrame', 'FXARestoreTypeStage']
        return click_btn(class_seq, {3: 2}, time_out_ts=10, btn_click=0)
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'ArchiveWizard', 'FXVerticalFrame', 'FXHorizontalFrame', 'FXVerticalFrame', 'FXARestoreTypeStage']
        return click_btn(class_seq, {4: 2}, time_out_ts=10, btn_click=0)


def pooling_welcome_page():
    class_seq = ['Desktop', 'FXATIShellWindow']
    return click_btn(class_seq, time_out_ts=10, btn_click=0)


def click_btn_reboot(current_os):
    if "XP" in current_os:
        class_seq = ['Desktop', 'FXVerticalFrame',
                     'FXHorizontalFrame', 'FXHorizontalFrame', 'FXButton']
        return click_btn(class_seq, {2: 2, 4: 2})
    elif "VISTA" in current_os or "WINDOWS 7" in current_os:
        class_seq = ['Desktop', 'FXAMessageBoxImpl', 'FXVerticalFrame',
                     'FXHorizontalFrame', 'FXHorizontalFrame', 'FXButton']
        return click_btn(class_seq, {3: 2, 5: 2})


def launch_acronis(exec_file):
    ret = trend.winProcessUtil.createProcess(exec_file)
    if ret == 0:
        return ErrorWin32ui.SUCCESS
    else:
        return ErrorWin32ui.FAIL


def restore_scenario_init(current_os):
    if pooling_welcome_page() == 0:
        click_btn_recovery_task(125, 185, current_os)
        click_btn_disk_recovery(160, 60, current_os)


def main_restory():
    """
       Main scenario for launch Acronis recovery
       B{Please install Acronis True Image Home 2010 first}
    """
    current_windows_info = trend.winVerUtil.WindowsVersion()
    current_os = current_windows_info.strProductName
    current_os = current_os.upper()

    launch_acronis(r"C:\Program Files\Acronis\TrueImageHome\TrueImage.exe")
    sleep(30)
    print thread.start_new_thread(restore_scenario_init, (current_os,))
    sleep(5)
    click_btn_archive_cancel(current_os)
    click_btn_archive_cancel(current_os)
    sleep(5)
    click_btn_archive_next(current_os)
    sleep(1)
    if pooling_archive_processing(current_os) == 0:
        sleep(1)
        click_btn_archive_next(current_os)
        sleep(1)
        select_dest_partition(30, 50, current_os)
        sleep(1)
        click_btn_archive_next(current_os)
        sleep(1)
        click_btn_archive_next(current_os)
        sleep(1)
        click_btn_proceed(current_os)
        sleep(60)
        if pooling_warning_box() == 0:
            click_btn_reboot(current_os)

if __name__ == '__main__':
    main_restory()
