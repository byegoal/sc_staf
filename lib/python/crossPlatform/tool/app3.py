import logging
import time
import call_staf_service
import gettext
_ = gettext.gettext


def monitor(connector, progress, machinelist):
    logger = logging.getLogger(__name__)
    objStafService = call_staf_service.StafService()
    colorEmpty = []
    for item in machinelist:
        colorEmpty.append('')

    while(1):
        progress.set(0, 10)
        for i in range(100, 0, -10):
            logger.info(_('Countdown value is %i'), i)
            # detect client
            intIndex = 0
            color = colorEmpty
            for item in machinelist:
                logger.info(_("staf ping ") + item)
                if objStafService.callStafService(item, "ping", "ping") != 0:
                    color[intIndex] = 'red'
                else:
                    # do more staf ping from clinet to server
                    import socket
                    serverip = socket.gethostbyname(socket.gethostname())
                    strParam = "start command cmd params \"/C staf %s ping ping\" wait" % serverip
                    if objStafService.callStafService(item, "process", strParam) != 0:
                        color[intIndex] = 'red'
                    else:
                        color[intIndex] = 'green'
                progress.tick(color)
                connector.ack()  # can be ommitted in this program
                color[intIndex] = ''
                print color
                intIndex = intIndex + 1
        logger.info(_('Done!'))


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    class dummy:
        def ack(self):
            pass

        def set(self, a, b):
            pass

        def tick(self, color):
            pass
    monitor(dummy(), dummy())
