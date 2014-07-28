'''
Created on 2011/10/21

@author: eason_lin
'''
import os
import sys
if __name__ == '__main__':
    args = " ".join(sys.argv[1:])
    print args
    TIMES = 3
    if TIMES > 0:
        os.system(args)
        NEED_TIMES = TIMES - 1
        for i in range(NEED_TIMES):
            #if not os.path.exists("C:\\STAF\\testsuites\\agentBVT\\fail_list.txt"):
            #    break
            os.system("%s -f C:\\STAF\\testsuites\\agentBVT\\fail_list.txt" %
                      args)
