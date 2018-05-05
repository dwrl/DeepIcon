#!/usr/bin/python

import efl.elementary as elm
from efl.elementary.window import StandardWindow
from efl.elementary.box import Box

from deepicon import *



class MyWindow(StandardWindow):
    def __init__(self):
        StandardWindow.__init__(self, "ex2", "Deep Icon Test")

        self.callback_delete_request_add(lambda o: elm.exit())

        bx = Box(self)

        ic1 = DeepIcon(self, 'terminal', 72)
        ic1.show()
        bx.pack_end(ic1)

        ic2 = DeepIcon(self, 'folder', 96)
        ic2.show()
        bx.pack_end(ic2)

        ic3 = DeepIcon(self, 'audio-mp3', 112)
        ic3.show()
        bx.pack_end(ic3)

        ic4 = DeepIcon(self, 'audio-mp3', 112)
        ic4.show()
        bx.pack_end(ic4)

        ic5 = DeepIcon(self, 'close', 146)
        ic5.show()
        bx.pack_end(ic5)

        self.content_set(bx)

if __name__ == "__main__":
    elm.init()

    myWin = MyWindow()
    myWin.show()

    elm.run()
    elm.shutdown()