"""
wrapped win32 utility to find window or other utility for UI automation
"""
import time
import logging
import win32api
import win32gui
import win32con
from errorCode import ErrorWin32ui


def findwindow(parent_handle, str_classname='', str_windowid='',
               str_partial_title="", int_instance_number=0, time_out=0, intRecursive=1,
               intWidth='', intHeight='', intInaccuracy=30):
    """
    use win32 api getwindow to get window handle by str_classname and str_partial_title
    support recursive finding children
    parameter is complicated, recommend to wrapper this function for easier use
    @param parent_handle: parent window handle, "Desktop" is special value to get desktop's handle
    @param str_classname: class name of window
    @param str_windowid:  id of window
    @param int_instance_number: (Suggest to combine with str_classname)
                                for the same str_classname, get the xth instance.
                                0 means doesn't care
    @param time_out:retry to find handle every 1 second until time_out
    @param intWidth & intHeight: specify the window size
    @param intInaccuracy: allow how much inaccuracy when checking window size (intWidth & intHeight)

    @return: return handle unmber if found matched window,
             ErrorWin32ui.HANDLE_NOT_FIND means not found
    """
    trytime = 0
    while (trytime <= time_out):
        #the first try doesn't need to sleep
        if trytime != 0:
            time.sleep(1)
        trytime = trytime + 1
        #if not specified, parent is desktop
        if parent_handle == "Desktop":
            hwnd = win32gui.GetWindow(
                win32gui.GetDesktopWindow(), win32con.GW_CHILD)
        #specific handle as parent
        else:
            hwnd = win32gui.GetWindow(int(parent_handle), win32con.GW_CHILD)

        current_instance_number = 1
        while hwnd != 0:
            if intRecursive == 1:
                #recursive to find children's chidren, if match, return handle
                target_handle = findwindow(hwnd, str_classname, str_windowid,
                                           str_partial_title, int_instance_number, time_out=0)
                if target_handle != ErrorWin32ui.HANDLE_NOT_FIND:
                    return target_handle

            #check if class name matches str_classname (if specific)
            if str_classname != "":
                classname = win32gui.GetClassName(hwnd)
                if classname != str_classname:
                    #traverse next child
                    hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
                    continue

            #pass class name check, compare instance unmber (if specific)
            if int_instance_number != 0:
                if current_instance_number != int_instance_number:
                    #instance +1, because str_classname matches
                    current_instance_number = current_instance_number + 1
                    #traverse next child
                    hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
                    continue

            #check if windows id matches str_windowid (if specific)
            if str_windowid != "":
                current_window_id = win32gui.GetWindowLong(
                    hwnd, win32con.GWL_ID)
                if str_windowid != str(current_window_id):
                    #traverse next child
                    hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
                    continue

            #check if windows title includes str_partial_title (if specific)
            if str_partial_title != "":
                str_title = win32gui.GetWindowText(hwnd)
                if not str_partial_title in str_title:
                    #traverse next child
                    hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
                    continue

            #check if window size matches intWidth and intHeight (if specific)
            if intWidth != "" and intHeight != "":
                rectInfo = win32gui.GetWindowRect(hwnd)
                intActualWidth, intActualHeight = rectInfo[2] - \
                    rectInfo[0], rectInfo[3] - rectInfo[1]
                logging.info('Windows Title: %s' %
                             win32gui.GetWindowText(hwnd))
                logging.info('intActualWidth: %d' % intActualWidth)
                logging.info('intActualHeight: %d' % intActualHeight)
                logging.info('intInaccuracy: %d' % intInaccuracy)
                logging.info('Width difference: %d' % abs(
                    intWidth - intActualWidth))
                logging.info('Height difference: %d' % abs(
                    intHeight - intActualHeight))

                if abs(intWidth - intActualWidth) > intInaccuracy or abs(intHeight - intActualHeight) > intInaccuracy:
                    #traverse next child
                    hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
                    continue

            #pass all check
            logging.info("Find window handle=%s, class='%s' id='%s' title='%s' instancenumber='%i'", hex(hwnd), str_classname, str_windowid, str_partial_title, int_instance_number)
            return hwnd

    #can not find window
    #logging.debug("Time out, can't find window class='%s' id='%s' title='%s'"\
    #              , str_classname, str_windowid, str_partial_title)
    return ErrorWin32ui.HANDLE_NOT_FIND


def findwindow_by_id(parent_handle, str_classname='', str_windowid='', time_out=0):
    """
    please reference to findwindow
    """
    return findwindow(parent_handle, str_classname=str_classname, str_windowid=str_windowid, time_out=time_out)


def findwindow_by_partial_title(parent_handle, str_classname, str_partial_title="", time_out=0):
    """
    please reference to findwindow
    """
    return findwindow(parent_handle, str_classname=str_classname, str_partial_title=str_partial_title, time_out=time_out)


def findwindow_by_class(parent_handle, str_classname, int_instance_number=0, time_out=0, intRecursive=1):
    """
    please reference to findwindow
    @param int_instance_number: for the same str_classname, get the xth instance.
                                0 means doesn't care
    """
    return findwindow(parent_handle, str_classname=str_classname, int_instance_number=int_instance_number, time_out=time_out, intRecursive=intRecursive)


def click_button(button_handle, parent_handle, action, xpos, ypos):
    """
    use win32 api SendMessage to
    @param button_handle: handle of button, can be get by findwindow
    @param parent_handle: handle of button's parent, it is for WM_PARENTNOTIFY use
    @param action: wrapped mousc action, ex. Left_Click
    @param xpos: x position of button to click
    @param ypos: y position of button to click
    @return: when success, return ErrorWin32ui.SUCCESS
             else, return ErrorWin32ui.FAIL
    """
    if action == "Left_Click":
        try:
            win32api.SendMessage(button_handle, win32con.WM_PARENTNOTIFY, win32con.WM_LBUTTONDOWN, win32api.MAKELONG(xpos, ypos))
            win32api.SendMessage(button_handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(xpos, ypos))
            win32api.SendMessage(button_handle, win32con.WM_MOUSEACTIVATE, parent_handle, win32api.MAKELONG(win32con.HTCLIENT, win32con.WM_LBUTTONDOWN))
            win32api.SendMessage(button_handle, win32con.WM_PARENTNOTIFY, win32con.WM_LBUTTONUP, win32api.MAKELONG(xpos, ypos))
            win32api.SendMessage(button_handle, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(xpos, ypos))
            win32api.SendMessage(button_handle, win32con.WM_MOUSEACTIVATE, parent_handle, win32api.MAKELONG(win32con.HTCLIENT, win32con.WM_LBUTTONDOWN))
            return ErrorWin32ui.SUCCESS
        except WindowsError:
            logging.error("Can't click button")
            logging.error(traceback.format_exc())
            return ErrorWin32ui.FAIL

    else:
        logging.error("Action %s is not supported", action)
        return ErrorWin32ui.FAIL


def Tab_Key(hwnd, intTabNum):
    """
        Simulate click Tab key in "intTabNum" times from keyboard
        @type hwnd: String
        @param hwnd: The Window handler
        @type intTabNum: Integer
        @param intTabNum: 1,2,3...
    """
    setForegroundWindow(hwnd)
    for i in range(intTabNum):
        time.sleep(1)
        win32api.keybd_event(win32con.VK_TAB, 0x45,
                             win32con.KEYEVENTF_EXTENDEDKEY | 0, 0)
        win32api.keybd_event(win32con.VK_TAB, 0x45, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP | 0, 0)
    return ErrorWin32ui.SUCCESS


def Enter_Key(hwnd):
    """
        Simulate click Enter key from keyboard
        @type hwnd: String
        @param hwnd: The Window handler
    """
    setForegroundWindow(hwnd)
    win32api.keybd_event(
        win32con.VK_RETURN, 0x45, win32con.KEYEVENTF_EXTENDEDKEY | 0, 0)
    win32api.keybd_event(win32con.VK_RETURN, 0x45,
                         win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP | 0, 0)
    return ErrorWin32ui.SUCCESS


def input_editbox(editbox_handle, str_text):
    win32api.SendMessage(editbox_handle, win32con.WM_SETTEXT, 0, str(str_text))


def setForegroundWindow(intHandle, intTimeout=10):
    """
    retry to set foreground
    @note:
    setForeground(0xab302, 10)
    @require:
    windows, pythonwin
    @param intHandle: handle to in
    @return:ErrorWin32ui.SUCCESS - success
            ErrorWin32ui.FAIL - fail
    """
    intTimeCounter = 0
    boolSetforeground = 0
    while boolSetforeground == 0 and intTimeCounter < intTimeout:
        try:
            win32gui.SetForegroundWindow(intHandle)
        except:
            time.sleep(1)
            intTimeCounter = intTimeCounter + 1
        else:
            boolSetforeground = 1
    if boolSetforeground == 1:
        return ErrorWin32ui.SUCCESS
    else:
        return ErrorWin32ui.FAIL

if __name__ == '__main__':
    #findwindow_by_class('MsiDialogCloseClass', 'Trend Micro Internet Security', 'Static', 'Successfully Uninstalled')
    print "findwindow, id is " + str(hex(findwindow(
        "Desktop", "WebViewHost", intWidth=100, intHeight=400)))
