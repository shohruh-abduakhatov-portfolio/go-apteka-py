import asyncio

from modules.kinetic_core.AbstractExecutor import AbstractExecutor
from .CpUserDB import CpUserDB

class CpUserExecutor(AbstractExecutor):

    async def login(self, login, password):
        if login is None:
            return self._error("login required")

        if password is None:
            return self._error("password required")

        user = await self._validate(login, password)
        if user is None:
            return self._error("invalid credential")
        else:
            print("publish")
            print(user)
            return user

    async def logout(self, data):
        pass

    async def _validate(self, login, password):
        db = CpUserDB()
        has = await db.login(login, password)
        if has:
            return {"status": "success", "data": has}
        else:
            return None

    @staticmethod
    def _error(message):
        return {"status": "fail", "message": message}
