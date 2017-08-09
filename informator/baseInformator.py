# -*- coding: utf-8 -*-
#!/usr/bin/env python
##### System wide lib #####
from abc import ABCMeta, abstractmethod
import codecs
from fabric.api import run, cd, sudo, hide, settings, local, lcd
from fabric.contrib.files import exists as fabExists
from fabric.operations import get, put

import os

##### Theory lib #####

##### Theory third-party lib #####

##### Local app #####

##### Theory app #####

##### Misc #####

class BaseInformator(object):
  __metaclass__ = ABCMeta
  debDepLst = []
  modDepLst = []
  requiredParamKeyLst = []
  bashProfile = ".bashrc"
  extraKwargs = []
  restartSrvLst = []

  def __init__(self, **kwargs):
    self.formData = kwargs.get("formData")
    for i in self.extraKwargs:
      setattr(self, i, self.formData["extraKwargs"][i])
    print "Starting {0}".format(self.__class__.__name__)

  @classmethod
  def aptKeyInstaller(self):
    pass

  def getKlassName(self):
    return self.__class__.__name__[:-9]

  def start(self):
    print "==>", self.getKlassName()
    return "{0}Ready".format(
        self.getKlassName()
        )

  def stop(self):
    print "==>", self.getKlassName()
    return "{0}Finish".format(
        self.getKlassName()
        )

  def restart(self, cfg):
    self.stop()
    self.start()

  def _initDir(self, dirPath, usrName, grpName):
    if not fabExists(dirPath):
      sudo("mkdir -p '{0}'".format(dirPath))
    sudo("chown -R {0}.{1} '{2}'".format(usrName, grpName, dirPath))

  def _cpOrReplaceFile(
      self,
      root,
      name,
      tmpDirPath,
      destPath,
      cfg
      ):
    # It is used to replace all var inside a given tmpl file and/or copy the
    # file to a temp dir for further process.
    local('mkdir -p "{0}/{1}"'.format(
      tmpDirPath,
      destPath,
      ))
    if name.endswith(".tmpl"):
      d = codecs.open("{0}/{1}".format(root, name), "r", "utf-8").read()
      d = d.format(**cfg)
      with codecs.open(
          "{0}/{1}/{2}".format(tmpDirPath, destPath, name[:-5]),
          "w",
          "utf-8"
          ) as fd:
        fd.write(d)
      permission = int(oct(
          os.stat("{0}/{1}".format(root, name)).st_mode
          & 0777), 8)
      name = name[:-5]
      os.chmod(
          "{0}/{1}/{2}".format(tmpDirPath, destPath, name),
          permission
          )
    else:
      local('cp -rf "{0}/{1}" "{2}/{3}"'.format(
        root,
        name,
        tmpDirPath,
        destPath,
        ))

  def preResDir(self):
    pass

  def prepareResDir(self, tmpDirPath, cfg):
    # To get all files for each Informator's specific config dir
    subDirName = self.__class__.__name__[:-10]
    subDirName = subDirName[0].lower() + subDirName[1:]
    print "prepare res dir({0}) to {1}".format(subDirName, tmpDirPath)
    rootDir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "config",
        subDirName
        )
    rootDirLen = len(rootDir)

    fileNum = 0
    for root, dirLst, fileLst in os.walk(rootDir, topdown=False):
      for name in fileLst:
        destPath = root[rootDirLen + 1:].format(**cfg)
        self._cpOrReplaceFile(
            root,
            name,
            tmpDirPath,
            destPath,
            cfg
            )
        fileNum += 1
    if fileNum > 0:
      return True
    else:
      return False

  def createUsrGrp(self, cfg):
    pass

  def postInst(self, cfg):
    pass

  def validateInst(self, cfg):
    return True

