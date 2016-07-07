# -*- coding: utf-8 -*-
#!/usr/bin/env python
##### System wide lib #####
import json
import re

##### Theory lib #####

##### Theory third-party lib #####

##### Local app #####

##### Theory app #####

##### Misc #####

class ConfigMixin(object):
  @staticmethod
  def _fillInConfig(cfg):
    varPattern = re.compile(r"{([\w_]+)}")

    keyLst = cfg.keys()

    try:
      cfg["projId"] = cfg["projName"] \
          + cfg["deployEnv"][0].upper() \
          + cfg["deployEnv"][1:]
    except:
      pass

    def getV(k):
      reResult = varPattern.search(str(cfg[k]))
      if reResult is not None:
        r = cfg[k]
        for i in reResult.groups():
          r = r.replace("{" + i + "}", getV(i))
        cfg[k] = r

      try:
        del keyLst[k]
      except:
        pass
      return cfg[k]

    while(len(keyLst) > 0):
      k = keyLst.pop()
      cfg[k] = getV(k)

    return cfg

  @staticmethod
  def _cleanCfg(cfg):
    cfg = cfg.replace("<br/>", "").replace("&quot;", '"')
    return json.loads(cfg)
