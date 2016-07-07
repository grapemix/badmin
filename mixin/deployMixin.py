# -*- coding: utf-8 -*-
#!/usr/bin/env python
##### System wide lib #####
from collections import OrderedDict
from fabric.api import run, cd, sudo, hide, settings
from fabric.operations import get, put
from tempfile import mkstemp
import os
import tarfile
from uuid import uuid4

##### Theory lib #####
from theory.utils.formats import bytes2human
from theory.utils.importlib import importModule

##### Theory third-party lib #####

##### Local app #####
from badmin.mixin.configMixin import ConfigMixin

##### Theory app #####

##### Misc #####

class DeployMixin(ConfigMixin):
  def _findInformator(self, informatorNameLst):
    informatorLst = self._findRecursiveInformator(informatorNameLst)
    informatorLst.reverse()
    return OrderedDict(informatorLst)

  def _findRecursiveInformator(self, informatorNameLst):
    childrenInformatorLst = []
    for i in informatorNameLst:
      klass = getattr(
          importModule(
            "badmin.informator.{0}".format(i[0].lower() + i[1:])
            ),
          i
          )
      childrenInformatorLst.append((i, klass))
      childrenInformatorLst.extend(
          self._findRecursiveInformator(klass.modDepLst)
      )
    return childrenInformatorLst

  def _scpResDir(self, tmpDirPath, bkDir="/tmp"):
    print("Preparing copying all resources file to the remote host")
    def savePermission(tarinfoObj):
      tarinfoObj.mode = int(oct(os.stat(
          os.path.join(tmpDirPath, tarinfoObj.path)
          ).st_mode & 0777), 8)
      if tarinfoObj.path.startswith("etc/"):
        #tarinfoObj.uid = tarinfoObj.gid = 0
        tarinfoObj.uname = "root"
        tarinfoObj.gname = "root"
      else:
        tarinfoObj.uname = self.formData["host"].username
        tarinfoObj.gname = "users"
      return tarinfoObj

    try:
      tmpFileTuple = mkstemp()
      with tarfile.open(tmpFileTuple[1], "w:gz") as tar:
        for i in os.listdir(tmpDirPath):
          tar.add(
              os.path.join(tmpDirPath, i),
              arcname=i,
              filter=savePermission
              )
      remoteTmpDirPath = "/tmp/{0}".format(uuid4())
      run("mkdir -p {0}".format(remoteTmpDirPath))
      sudo("mkdir -p {0}".format(bkDir))
      sudo("chown {0}.users {1}".format(
        self.formData["host"].username,
        bkDir))

      print "Uploaded package size: {0}".format(
          bytes2human(os.path.getsize(tmpFileTuple[1]))
          )
      put(tmpFileTuple[1], "{0}/a.tgz".format(remoteTmpDirPath))
      #with cd(remoteTmpDirPath):
      #  run("tar xvfz {0}/a.tgz".format(remoteTmpDirPath))
      #  run("rm a.tgz")
      #  sudo("cp -prf ./* /")
      with cd("/"):
        with hide('running', 'stdout'):
          sudo("tar xvfz {0}/a.tgz".format(remoteTmpDirPath))

      run("mv {0}/a.tgz {1}/badminBackup.tgz".format(remoteTmpDirPath, bkDir))
      run("rm -rf {0}".format(remoteTmpDirPath))
    except Exception as e:
      print e
    finally:
      os.remove(tmpFileTuple[1])

  def _installDeb(self, debLst):
    print "Installing deb now...."
    print debLst
    if len(debLst) > 0:
      with hide("output"):
        sudo("apt-get update")
        sudo("apt-get --yes --force-yes install %s" % (" ".join(debLst)))
