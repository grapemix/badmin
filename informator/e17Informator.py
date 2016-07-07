# -*- coding: utf-8 -*-
#!/usr/bin/env python
##### System wide lib #####
#from fabric.api import sudo
from fabric.contrib.files import append as fabricFileAppend

##### Theory lib #####

##### Theory third-party lib #####

##### Local app #####
from badmin.informator.baseInformator import BaseInformator

##### Theory app #####

##### Misc #####

class E17Informator(BaseInformator):
  #debDepLst = [
  #    "e17-dev", "libelementary-dev", "python-elementary",
  #    "python-evas", "python-edje" ,"python-ethumb", "python-ecore",
  #    "python-edbus", "python-dev", "build-essential"
  #]
  #debDepLst = ["bodhi-desktop",]
  debDepLst = [
      "elementary", "python-elementary",
      "python-evas", "python-edje" ,"python-ethumb", "python-ecore",
      "python-dev", "build-essential"
  ]

  #@classmethod
  #def aptKeyInstaller(self):
  #  sudo("add-apt-repository -y ppa:efl/trunk")
  #  #sudo("add-apt-repository -y ppa:vase/ppa")

  @classmethod
  def aptKeyInstaller(self):
    fabricFileAppend(
        "/etc/apt/sources.list",
        "deb http://packages.bodhilinux.com/bodhi trusty main",
        use_sudo=True
        )

