# region import
import os
import subprocess

from modules.pharmex.utils.exception_handler import *
from web.handlers.BaseHandler import *


class WebhookHandler(BaseHandler):
    repo = "git@bitbucket.org:anton_vasiljev/vita-control-panel.git"


    # @throws_handler()
    async def post(self):
        repo = self.get_argument("repo")
        print("webhook: ", repo)
        print(self)
        if repo is None or repo != repo: return
        p = os.path.abspath(__file__ + "/../../../../reload.sh")
        subprocess.Popen(["sh", p])
        sys.exit(-1)
