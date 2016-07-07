# -*- coding: utf-8 -*-
#!/usr/bin/env python
##### System wide lib #####
from fabric.api import run, cd, sudo, hide, settings
from fabric.contrib.files import append as fileAppend
from fabric.contrib.files import contains as fileContains
from fabric.contrib.files import exists as fileExists
from fabric.operations import get, put

import os
from shutil import rmtree
import tarfile
from tempfile import mkdtemp

##### Theory lib #####

##### Theory third-party lib #####

##### Local app #####
from badmin.informator.baseInformator import BaseInformator

##### Theory app #####

##### Misc #####

class TheoryDevInformator(BaseInformator):
  debDepLst = [
      "git",
      "git-flow",
      "vim-gtk",
      "screen",
      "python-dev",
      "build-essential",
      "python-virtualenv",
      "virtualenvwrapper",
      # for hstore
      "postgresql-contrib",
      ]
  modDepLst = ["TheoryInformator", ]
  requiredParamKeyLst = [
      "home",
      "projRoot",
      "projName",
      "venvName",
      "venvPath",
      "theoryUsername",
  ]

  def __init__(self, *args, **kwargs):
    super(TheoryDevInformator, self).__init__(*args, **kwargs)

  def _patchBash(self):
    bashProfile = self.bashProfile
    with cd("~"):
      if(not fileExists(bashProfile)):
        run("touch %s" % bashProfile)
      if(not fileContains(bashProfile, "WORKON_HOME")):
        run("echo 'export WORKON_HOME={0}'/venv >> {1}".format(
          self.projRoot,
          bashProfile
          ))
      if(not fileContains(bashProfile, "VIRTUALENVWRAPPER_HOOK_DIR")):
        run(
            "echo 'export VIRTUALENVWRAPPER_HOOK_DIR=$WORKON_HOME' >> %s" \
                % (bashProfile)
        )
      if(not fileContains(bashProfile, "THEORY_SETTINGS_MODULE")):
        run("echo 'export THEORY_SETTINGS_MODULE={0}.settings' >> {1}".format(
          self.venvName,
          bashProfile
          ))
      if(not fileContains(
          bashProfile,
          "PYTHONPATH[-a-zA-Z_0-9/:]*{0}/project[-a-zA-Z_0-9/:]*"\
              .format(self.projRoot),
          escape=False,
          )):
        run("echo 'export PYTHONPATH=$PYTHONPATH:{0}/project:' >> {1}".format(
          self.projRoot,
          bashProfile
          ))
      if(not fileContains(bashProfile, "virtualenvwrapper")):
        run(
            "echo 'source /etc/bash_completion.d/virtualenvwrapper' >> %s" \
                % (bashProfile)
        )

  def _installTheory(self, path, cfg):
    with cd(path):
      with hide("output"):
        if(not fileExists(os.path.join(path, "theory"))):
          run("git clone git://github.com/grapemix/theory.git")
        else:
          # we already cd to home dir in above
          with cd("theory"):
            run("git pull")
    with cd(os.path.join(path, "theory")):
      run("git checkout develop")

    with cd(path):
      #run("""
      #    . {0}/{1}/bin/activate;
      #    easy_install theory/
      #    """\
      #    .format(self.venvPath, self.venvName)
      #)
      run("""
          . {venvPath}/{venvName}/bin/activate;
          pip install -e theory/;
          pip install celery simplejson ludibrio psycopg2 ipdb gevent;
          """\
          .format(**cfg)
      )

  #def _copyConfigFileLst(self):
  #  print "Copy config file"
  #  try:
  #    tmpDir = mkdtemp()  # create dir
  #    tar = tarfile.open(
  #        os.path.join(
  #          os.path.dirname(os.path.dirname(__file__)),
  #          "config",
  #          "devBusyBox.tgz"
  #          )
  #        )
  #    tar.extractall(path=tmpDir)
  #    tar.close()

  #    for i in os.listdir(tmpDir):
  #      put(os.path.join(tmpDir, i), self.configFileLst[i])

  #    run("chmod 755 {0}/{1}".format(self.projRoot, "dev.sh"))

  #    sudo("mv {0}/theory_start.py /usr/local/bin/".format(self.projRoot))
  #    sudo("chmod 755 /usr/local/bin/theory_start.py")
  #  finally:
  #    try:
  #      rmtree(tmpDir)  # delete directory
  #    except OSError as exc:
  #      if exc.errno != 2:  # code 2 - no
  #        raise

  #def _copyConfigFileLst(self):
  #  print "Copy config file"
  #  print self.__class__.__name__
  #  subDirName = self.__class__.__name__[:-10]
  #  print subDirName
  #  subDirName = subDirName[0].lower() + subDirName[1:]
  #  print subDirName
  #  rootDir = os.path.join(
  #      os.path.dirname(os.path.dirname(__file__)),
  #      "config",
  #      subDirName
  #      )

  #  for name in os.listdir(rootDir):
  #    if name in self.configFileLst:
  #      loc, owner = self.configFileLst[name]
  #      if owner is not None:
  #        put(os.path.join(rootDir, name), "/tmp", mirror_local_mode=True)
  #        sudo("mv /tmp/{0} {1}".format(name, loc))
  #        sudo("chown -R {0} {1}/{2}".format(owner, loc, name))
  #      else:
  #        put(os.path.join(rootDir, name), loc, mirror_local_mode=True)

  def _setupVenv(self, cfg):
    run((
        "source /etc/bash_completion.d/virtualenvwrapper;"
        "WORKON_HOME={venvPath} "
        "VIRTUALENVWRAPPER_HOOK_DIR=$WORKON_HOME "
        "mkvirtualenv --no-site-packages {venvName}"
        ).format(**cfg)
    )
    self._installTheory("~", cfg)
    with cd("/opt"):
      sudo("rm -f theory")
      sudo("ln -s %s %s" %
          ("~/theory", "theory")
      )

    #pip install -r /opt/crystal/project/panel/requirement.pip
    #run("pip install theory")
    #installPath = run((
    #      ". {0}/{1}/bin/activate;"
    #      'python -c "import theory; print theory.__path__[0];"'
    #    ).format(self.venvPath, self.venvName))
    #print installPath
    #if "site-packages" not in installPath:
    #  installPath = "{0}/{1}/src/theory".format(self.venvPath, self.venvName)
    #elif installPath.endswith("theory"):
    #  installPath = installPath[:-7]

    #print "rm -rf {0}/theory".format(installPath)
    #run("rm -rf {0}/theory".format(installPath))
    #run("rm -rf {0}/tests".format(installPath))
    ##run("mkdir -p {0}/theory".format(installPath))

    #installPath = "~/"
    #with cd(installPath):
    #  run("ln -s /opt/theory/theory theory")
    #  run("ln -s /opt/theory/tests tests")

  def _copyTheoryProjectTemplate(self, cfg):
    run(
        "mkdir -p {projRoot}/project/{venvName}/settings".format(**cfg)
    )
    run(
        "mkdir -p {projRoot}/project/{venvName}/logs".format(**cfg)
    )
    run(
        "touch {projRoot}/project/{venvName}/__init__.py".format(**cfg)
    )
    run(
        "mkdir -p {projRoot}/mood".format(**cfg)
    )
    with cd("/opt/theory/theory/conf"):
      run("""
          cp -rf project_template/settings.py {projRoot}/project/{venvName}/settings/base.py
          """\
          .format(**cfg))
      run("""
          cp -rf project_template/__init__.py {projRoot}/project/{venvName}/settings/
          """\
          .format(**cfg))
      run("cp -rf mood_template {projRoot}/mood/norm".format(**cfg))

    run("bash ~/patch.sh")
    fileAppend(
        "/opt/crystal/mood/norm/config.py",
        'RESOLUTION = (("640", "480"),)'
        )

  def postInst(self, cfg):
    print "TheoryDevInformator post install"
    self.projRoot = cfg["projRoot"]
    self.venvName = cfg["venvName"]

    sudo("mkdir -p {venvPath}".format(**cfg))
    sudo("chown {theoryUsername} -R {projRoot}".format(**cfg))

    #self._copyConfigFileLst()
    self._patchBash()
    self._setupVenv(cfg)
    self._copyTheoryProjectTemplate(cfg)


