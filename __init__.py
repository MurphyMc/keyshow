from pox.core import core
from pox.web.webcore import InternalContentHandler
from pox.web.websocket import WebsocketHandler
from pox.lib.revent import Event, EventMixin

import os
import json
import cgi

log = core.getLogger()

shows_dir = os.path.join(os.path.split(__file__)[0], "shows")

PLAYER_NAME = "assets/player/KeynoteDHTMLPlayer.html"


class KSCmd (Event):
  def __init__ (self, cmd):
    self.cmd = cmd

class KSStatusInfo (Event):
  def __init__ (self, info):
    self.info = info


class Keyshow (EventMixin):
  _eventMixin_events = set([KSCmd, KSStatusInfo])
  last_info = {}

  def set_info (self, info):
    self.last_info = info
    self.raiseEvent(KSStatusInfo(info))


class ControllerHandler (WebsocketHandler):
  def _on_message (self, op, msg):
    msg = json.loads(msg)
    if "cmd" in msg:
      core.Keyshow.raiseEvent(KSCmd(msg["cmd"]))

  def _on_start (self):
    log.debug("Controller Connected")
    core.Keyshow.addListeners(self, weak=True)
    if core.Keyshow.last_info:
      self.send({"status_info": core.Keyshow.last_info})

  def _on_stop (self):
    pass

  def _handle_KSStatusInfo (self, event):
    log.info("KSStatusInfo", event.info)
    self.send({"status_info": event.info})


class AgentHandler (WebsocketHandler):
  def _on_message (self, op, msg):
    msg = json.loads(msg)
    if "slide_info" in msg:
      core.Keyshow.raiseEvent(KSStatusInfo(msg))

  def _on_start (self):
    log.debug("Agent Connected")
    core.Keyshow.addListeners(self, weak=True)

  def _handle_KSCmd (self, event):
    self.send({"cmd": event.cmd})

  def _on_stop (self):
    pass


def _handle_WebRequest (event):
  if event.handler.prefix != "/keyshow/shows": return
  p = event.handler.path
  if not p.startswith("/"): return
  p = p[1:].split("/", 1)
  if len(p) != 2: return
  s,p = p
  if not p == PLAYER_NAME: return
  if not is_valid_show(s): return

  with open(os.path.join(shows_dir, s, PLAYER_NAME), "rb") as f:
    content = f.read()
  content = content.replace(b"</head>", b"""
        <script>Keyshow_ShowName = '%s';</script>
        <script type="text/javascript" src="/keyshow/www/resocket.js"></script>
        <script type="text/javascript" src="/keyshow/www/agent.js"></script>
        </head>""" % (s.encode(),))
  event.set_handler(InternalContentHandler)
  event.handler.args = {None: ("text/html", content)}
  log.info("Injected agent into %s", s)


def is_valid_show (s):
  if "." in s or "/" is s or "\\" in s or os.path.sep in s: return False
  s = os.path.join(shows_dir, s)
  if not os.path.isdir(s): return False
  if not os.path.exists(os.path.join(s, "index.html")): return False
  if not os.path.isfile(os.path.join(s, PLAYER_NAME)): return False
  return True


def list_show_page (request):
  shows = next(os.walk(shows_dir))[1]
  shows = [s for s in shows if is_valid_show(s)]

  o = "<a href='www/controller.html'>Open Remote</a>"
  o += "<ul>"
  for show in shows:
    o += ("<li><a href='shows/%s'>%s</a>" % (cgi.escape(show), show))
  o += "</ul>"

  o = ("<html><head><title>Keynote Shows</title></head>"
     + "<body>" + o + "<body></html>")

  return ("text/html", o)


def _setup ():
  addr = list(core.WebServer.socket.getsockname())

  docs = {'/': list_show_page}
  core.WebServer.set_handler("/keyshow", InternalContentHandler, docs)
  core.WebServer.add_static_dir('/keyshow/shows', 'shows', relative=True)
  core.WebServer.add_static_dir('/keyshow/www', 'www', relative=True)
  core.WebServer.set_handler("/keyshow/controller/ws", ControllerHandler)
  core.WebServer.set_handler("/keyshow/agent/ws", AgentHandler)

  core.WebServer.add_listener(_handle_WebRequest)

  for cmd in "next_build next_slide prev_build prev_slide".split():
    def make (cmd):
      core.Interactive.variables[cmd] = (
           (lambda:lambda: core.Keyshow.raiseEvent(KSCmd(cmd)))())
    make(cmd)


def launch ():
  core.registerNew(Keyshow)
  core.call_when_ready(_setup, ("WebServer",), "keyshow")
