#!/usr/bin/env python3
from __future__ import with_statement
from __future__ import print_function
import os
import tempfile

import cherrypy
from cherrypy import tools
from cherrypy import request

from swipl_expect_iface import run_swipl, PrologError

import traceback

cherrypy.config.update({"server.socket_port": 9884, "server.socket_host": "0.0.0.0"})

class PrologSite:
    @cherrypy.expose
    @tools.json_in()
    @tools.json_out()
    def run_swipl(self):
        if (len(request.json["queries"]) == 0):
          return {"status":"failure", "errormsg": "need at least one query (terminated by \".\")"}
        with tempfile.NamedTemporaryFile() as tmpfile:
          tmpfile.write(bytes(request.json["clauses"],"utf-8"))
          tmpfile.flush()
          try:
            swiplresult = run_swipl(tmpfile.name, request.json["queries"])
            return {"status": "ok", "data": swiplresult}
          except PrologError as e:
            return {"status": "failure", "errormsg": str(e)}


if __name__ == "__main__":
  STATIC_DIR = os.path.join(os.path.abspath("."), "static")

  config = {'/static':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': STATIC_DIR,
                }
         }

  cherrypy.tree.mount(PrologSite(), "/", config=config)

  cherrypy.engine.start()
  cherrypy.engine.block()
