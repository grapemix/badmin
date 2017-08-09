# -*- coding: utf-8 -*-
#!/usr/bin/env python
##### System wide lib #####
import datetime
from fabric.api import run, cd, sudo, hide, settings
from fabric.operations import get, put
import logging
from tempfile import mkdtemp
import os
from shutil import rmtree

##### Theory lib #####
from theory.apps.command.baseCommand import SimpleCommand
#from theory.apps.command.baseCommand import AsyncCommand
from theory.gui import field

##### Theory third-party lib #####

##### Local app #####
from badmin.mixin.deployMixin import DeployMixin
from badmin.model import Informator, Machine

##### Theory app #####

##### Misc #####

__all__ = ("Infect", )

class Infect(SimpleCommand, DeployMixin):
#class Infect(AsyncCommand):
  """ To infect other computer to use theory, mainly targeted for ubuntu.
  Have to manually do `sudo apt-get install openssh-server openssh-client`
  first
  """
  name = "infect"
  verboseName = "infect"

  #def _addSshAuth(self):
  #  keyPath = os.path.expanduser(self.formData["host"].keyRelPath)
  #  if keyPath is not None:
  #    run("mkdir -p .ssh")
  #    run("chmod 700 .ssh")
  #    put(
  #        keyPath,
  #        "~/.ssh/authorized_keys",
  #        mirror_local_mode=True
  #    )

  class ParamForm(SimpleCommand.ParamForm):
    host = field.ChoiceField(
        label="Machine host",
        choices=(set([(str(i.id), i.name) for i in Machine.objects.exclude(
          username=None
          )])),
        )
    informatorLst = field.MultipleChoiceField(
        choices=(set([(str(i.id), i.name) for i in Informator.objects.all()])),
        )
    extraKwargs = field.DictField(
        field.TextField(),
        field.TextField(),
        )

  def run(self, *args, **kwargs):
    self.formData = self.paramForm.clean()
    informatorNameLst = [
        "{0}Informator".format(
          i.name[0].upper() + i.name[1:]
          ) for i in Informator.objects.filter(
            id__in=self.formData["informatorLst"]
            )
        ]
    self.formData["host"] = Machine.objects.get(id=self.formData["host"])

    informatorLst = self._findInformator(informatorNameLst)
    print "The following packages are being installed: {0}"\
        .format(informatorNameLst)

    requiredParamKeySet = []
    for informator in informatorLst.values():
      requiredParamKeySet.extend(informator.requiredParamKeyLst)
    requiredParamKeySet = set(requiredParamKeySet)

    cfg = self.formData["extraKwargs"]
    if requiredParamKeySet - set(cfg.keys()) != set():
      cfg = {"sshKeyPath": self.formData["host"].keyRelPath}
      cfg.update(self._cleanCfg(self.formData["host"].proj.dict))
      cfg.update(self.formData["extraKwargs"])
    cfg = self._fillInConfig(cfg)
    cfg["updateLvl"] = int(cfg.get("updateLvl", 0))

    if i in requiredParamKeySet - set(cfg.keys()) != set():
      raise

    with settings(
        host_string=self.formData["host"].ip,
        user=self.formData["host"].username,
        key_filename=os.path.expanduser(self.formData["host"].keyRelPath)
        ):

      for informator in informatorLst.values():
        informator.aptKeyInstaller()

      # pkg installation has to come first because we don't want any files
      # in resource dir being overwritten by the files from pkg
      debDepLst = []
      for informator in informatorLst.values():
        debDepLst.extend(informator.debDepLst)

      if("updateLvl" not in cfg or cfg["updateLvl"] <= 1):
        self._installDeb(debDepLst)

      #buf = []
      #for informator in informatorLst:
      #  buf.append(informator(formData=self.formData))
      #informatorLst = buf

      for k, informator in informatorLst.iteritems():
        informatorLst[k] = informator(formData=self.formData)

      try:
        tmpDirPath = mkdtemp()
        emptyCfgInformatorNum = 0
        print "----"
        print ""
        for informatorName, informator in informatorLst.iteritems():
          print "PrepareResDir->{0}".format(informatorName)
          if not informator.prepareResDir(tmpDirPath, cfg):
            emptyCfgInformatorNum += 1
        print "----"
        for informatorName,informator in informatorLst.iteritems():
          print "PreResDir->{0}".format(informatorName)
          informator.preResDir()
        print "----"
        if emptyCfgInformatorNum == len(informatorLst):
          print "Skipping copying cfg because all informator has no cfg"
        else:
          if cfg.has_key("projRoot"):
            self._scpResDir(tmpDirPath, cfg["projRoot"])
          else:
            self._scpResDir(tmpDirPath)
      except Exception as e:
        print e
        raise
      finally:
        rmtree(tmpDirPath)


      for informatorName, informator in informatorLst.iteritems():
        informator.createUsrGrp(cfg)

      sudo("systemd-tmpfiles --create")

      #informatorLst.reverse()
      for informatorName, informator in informatorLst.iteritems():
        print informatorName
        informator.postInst(cfg)

      for informatorName, informator in informatorLst.iteritems():
        for restartInformatorName in informator.restartSrvLst:
          print "Restart->{0}".format(informatorName)
          informatorLst[restartInformatorName].restart(cfg)

      isAllRight = True
      for informator in informatorLst.values():
        if not informator.validateInst(cfg):
          isAllRight = False

      if isAllRight and cfg.has_key("revision"):
        self.formData["host"].image.deployRevision = cfg["revision"]
        self.formData["host"].image.lastUpdate = datetime.datetime.now()
        self.formData["host"].image.save()
      print "DONE"
