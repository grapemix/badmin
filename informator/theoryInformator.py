# -*- coding: utf-8 -*-
#!/usr/bin/env python
##### System wide lib #####

##### Theory lib #####

##### Theory third-party lib #####

##### Local app #####
from badmin.informator.baseInformator import BaseInformator

##### Theory app #####

##### Misc #####

class TheoryInformator(BaseInformator):
  modDepLst = ["E17Informator", "PostgresInformator",]
  debDepLst = [
      "git",
      "libevent-dev",
      "libpq-dev",
      "rabbitmq-server",
      "gir1.2-notify-0.7",
      ]


