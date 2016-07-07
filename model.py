# -*- coding: utf-8 -*-
#!/usr/bin/env python

##### System wide lib #####
import datetime

##### Theory lib #####
from theory.contrib.postgres.fields import ArrayField, HStoreField
from theory.db import model
from theory.utils.translation import ugettextLazy as _

##### Theory third-party lib #####

##### Local app #####

##### Theory app #####

##### Misc #####

class DeployLog(model.Model):
  proj = model.ForeignKey(
      "Project",
      verboseName=_("Project"),
      helpText=_("Project")
      )
  desc = model.TextField(
      verboseName=_("Description"),
      helpText=_("Description"),
      blank=True,
      null=True,
      )
  isSuccess = model.NullBooleanField()
  created = model.DateTimeField(default=datetime.datetime.utcnow())
  finished = model.DateTimeField(blank=True, null=True)

class Project(model.Model):
  name = model.CharField(
      maxLength=256,
      verboseName=_("Name"),
      helpText=_("Name of the project")
      )
  env = model.CharField(
      maxLength=24,
      verboseName=_("Environment"),
      helpText=_("Environment of the project")
      )
  dict = model.TextField(
      blank=True,
      null=True,
      )
  hivePlan = model.ForeignKey(
      "HivePlan",
      verboseName=_("HivePlan"),
      helpText=_("Hive plan"),
      blank=True,
      null=True
      )

  class Meta:
    uniqueTogether = (("name", "env"))

  def __str__(self):
    return "{0} - ${1}".format(self, name, self.env)

class Machine(model.Model):
  PHY_TYPE_HW = 1
  PHY_TYPE_CONTROLLER = 2
  PHY_TYPE_VM = 3

  PHY_TYPE_CHOICES = (
      (PHY_TYPE_HW, 'Hardware'),
      (PHY_TYPE_CONTROLLER, 'Controller'),
      (PHY_TYPE_VM, 'VM'),
      )

  name = model.CharField(
      maxLength=256,
      verboseName=_("Name"),
      helpText=_("Name of the informator")
      )
  ip = model.IPAddressField(
      verboseName="IP Address",
      helpText="The ip address being infected",
      blank=True,
      null=True,
      )
  username = model.CharField(
      maxLength=32,
      verboseName=_("Username"),
      helpText=_("Username. Blank if it is not ssh-able"),
      blank=True,
      null=True,
      )
  port = model.IntegerField(
      verboseName=_("Port"),
      helpText=_("Ssh port"),
      default=22,
      )
  macAddr = model.CharField(
      maxLength=24,
      verboseName=_("Mac Address"),
      helpText=_("Mac Address"),
      blank=True,
      null=True,
      )
  phyType = model.IntegerField(
      choices=PHY_TYPE_CHOICES,
      default=PHY_TYPE_HW,
      helpText=_("Physical Type"),
      )
  proj = model.ForeignKey(
      "Project",
      relatedName="machine",
      verboseName=_("Project"),
      helpText=_("Project"),
      )
  image = model.ForeignKey(
      "Image",
      blank=True,
      null=True,
      verboseName=_("Image"),
      helpText=_("Image")
      )
  identifier = model.CharField(
      blank=True,
      null=True,
      maxLength=36,
      verboseName=_("Identifier"),
      helpText=_("Identifier being used in cloud provider")
      )
  keyRelPath = model.CharField(
      maxLength=1024,
      verboseName=_("Key Relative Path"),
      helpText=_("The relative path of the private key to access the machine"),
      blank=True,
      null=True,
      )
  dict = HStoreField(
      blank=True,
      null=True,
      )
  created = model.DateTimeField(default=datetime.datetime.utcnow())
  touched = model.DateTimeField(
      default=datetime.datetime.utcnow()
      )
  class Meta:
    uniqueTogether = (("proj", "name"))

class Image(model.Model):
  name = model.CharField(
      maxLength=256,
      verboseName=_("Name"),
      helpText=_("Name of the informator")
      )
  loc = model.CharField(
      maxLength=512,
      verboseName=_("Location"),
      helpText=_("The image storage location"),
      unique=True,
      )
  stock = model.ForeignKey(
      "Image",
      blank=True,
      null=True,
      verboseName=_("Stock"),
      helpText=_("Stock which derived from")
      )
  informator = model.ManyToManyField(
      "Informator",
      blank=True,
      null=True,
      verboseName=_("Informator"),
      helpText=_("The deploy informator")
      )
  proj = model.ForeignKey(
      "Project",
      verboseName=_("Project"),
      helpText=_("Project")
      )
  #machine = model.ForeignKey(
  #    "Machine",
  #    blank=True,
  #    null=True,
  #    verboseName=_("Machine"),
  #    helpText=_("Machine")
  #    )
  keyRelPath = model.CharField(
      maxLength=1024,
      verboseName=_("Key Relative Path"),
      helpText=_("The relative path of the private key to access the machine"),
      blank=True,
      null=True,
      )
  dict = HStoreField(
      blank=True,
      null=True,
      )
  created = model.DateTimeField(default=datetime.datetime.utcnow())
  touched = model.DateTimeField(
      default=datetime.datetime.utcnow()
      )
  lastInformatorVersion = HStoreField(
      blank=True,
      null=True,
      )
  lastUpdate = model.DateTimeField(
      blank=True,
      null=True,
      )
  deployRevision = model.IntegerField(
      verboseName=_("Deploy revision"),
      helpText=_("Deploy revision"),
      default=1,
      )

  class Meta:
    uniqueTogether = (("proj", "name"))

class Repo(model.Model):
  REPO_TYPE_SRV = 1
  REPO_TYPE_APP = 2

  REPO_TYPE_CHOICES = (
      (REPO_TYPE_SRV, "Server"),
      (REPO_TYPE_APP, "Application"),
      )

  url = model.CharField(
      maxLength=2048,
      verboseName=_("Repository"),
      helpText=_("Repository URL"),
      )
  repoType = model.IntegerField(
      choices=REPO_TYPE_CHOICES,
      default=REPO_TYPE_SRV,
      helpText=_("Repository type"),
      )
  signature = model.TextField(
      verboseName=_("Signature"),
      helpText=_("Signature"),
      )

class Package(model.Model):
  UPDATE_POLICY_SECURITY_ONLY = 1
  UPDATE_POLICY_HOLD = 2
  UPDATE_POLICY_ALWAYS_UPDATE = 3
  UPDATE_POLICY_KEEP_COPY = 4

  UPDATE_POLICY_CHOICES = (
      (UPDATE_POLICY_SECURITY_ONLY, 'Update on security only'),
      (UPDATE_POLICY_HOLD, 'Hold on update'),
      (UPDATE_POLICY_ALWAYS_UPDATE, 'Always update'),
      (UPDATE_POLICY_KEEP_COPY, 'Keep a copy for this version'),
  )

  INSTALL_STATUS_UNINSTALL = 1
  INSTALL_STATUS_INSTALL = 2
  INSTALL_STATUS_BROKEN_UNINSTALL = 3
  INSTALL_STATUS_BROKEN_INSTALL = 4

  INSTALL_STATUS_CHOICES = (
      (INSTALL_STATUS_UNINSTALL, 'Uninstall'),
      (INSTALL_STATUS_INSTALL, 'Install'),
      (INSTALL_STATUS_BROKEN_UNINSTALL, 'Broken in uninstall'),
      (INSTALL_STATUS_BROKEN_INSTALL, 'Broken in install'),
  )

  name = model.CharField(
      maxLength=256,
      verboseName=_("Name"),
      helpText=_("Name of the informator")
      )
  version = model.IntegerField(
      verboseName=_("Version"),
      helpText=_("Version able to compare"),
      # Because this field will be automatically fill in
      default=0,
      )
  displayVersion = model.CharField(
      maxLength=32,
      verboseName=_("Display version"),
      helpText=_("Human readable version")
      )
  installStatus = model.IntegerField(
      choices=INSTALL_STATUS_CHOICES,
      default=INSTALL_STATUS_UNINSTALL,
      helpText=_("Instatll status"),
      )
  updatePolicy = model.IntegerField(
      choices=UPDATE_POLICY_CHOICES,
      default=UPDATE_POLICY_SECURITY_ONLY,
      helpText=_("Update policy"),
      )
  tagLst = ArrayField(
      model.TextField(),
      default=[],
      verboseName=_("Tag list"),
      helpText=_("Tag list for package"),
      blank=True,
      null=True,
      )

  created = model.DateTimeField(default=datetime.datetime.utcnow())
  touched = model.DateTimeField(
      default=datetime.datetime.utcnow()
      )

  class Meta:
    abstract = True

  def extractVersion(self):
    token = self.displayVersion.split(".")
    r = 0
    token.reverse()
    i = 1
    for t in token:
      r += int(t) * i
      i *= 10
    self.version = r

  def save(self, *args, **kwargs):
    self.extractVersion()
    super(Package, self).save(*args, **kwargs)


class Informator(Package):
  #repo = model.CharField(
  #    maxLength=2048,
  #    verboseName=_("Repository"),
  #    helpText=_("Repository URL"),
  #    blank=True,
  #    null=True,
  #    )
  dependent = model.ManyToManyField(
      "Informator",
      blank=True,
      null=True,
      relatedName="dependent",
      verboseName=_("dependent informator"),
      helpText=_("The dependent informator")
      )
  conflict = model.ManyToManyField(
      "Informator",
      blank=True,
      null=True,
      relatedName="conflict",
      verboseName=_("conflict informator"),
      helpText=_("The conflict informator")
      )

class HivePlan(Package):
  INFRA_TYPE_AWS = 1
  INFRA_TYPE_OPENSTACK = 2

  INFRA_TYPE_CHOICES = (
      (INFRA_TYPE_AWS, 'Aws'),
      (INFRA_TYPE_OPENSTACK, 'Openstack'),
  )

  infraType = model.IntegerField(
      choices=INFRA_TYPE_CHOICES,
      default=INFRA_TYPE_AWS,
      helpText=_("Infrastructure type"),
      )
