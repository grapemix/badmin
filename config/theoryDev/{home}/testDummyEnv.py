# -*- coding: utf-8 -*-
##### System wide lib #####
from efl import elementary
from efl.elementary.window import StandardWindow

##### Theory lib #####
from theory.gui.etk.element import Box

##### Theory third-party lib #####

##### Local app #####

##### Theory app #####

##### Misc #####

__all__ = ('getDummyEnv',)

def getDummyEnv():
  elementary.init()
  dummyWin = StandardWindow("test", "test win", autodel=True)

  # Copied from gui.etk.widget._createContainer
  dummyBx = Box()
  dummyBx.win = dummyWin
  dummyBx.generate()
  return (dummyWin, dummyBx)

