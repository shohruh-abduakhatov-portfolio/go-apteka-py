from modules.kinetic_core.AbstractDB import AbstractDB, table
import hashlib
from modules.kinetic_core.Connector import db

@table(name="pharmex_front_users", key="user_id")
class CpUserDB(AbstractDB):
    salt = "63ae0cf1ff064ac2b41d995ff8259913"
    async def login(self, login, password):
        pwd = hashlib.sha512((password + self.salt).encode('utf-8')).hexdigest()

        user = await db.query("select *, current_timestamp from pharmex_front_users where login = $1 and password = $2",
        (login, pwd,))

        if user is not None:
            return {"user": user}
        else:
            return None

    async def get_by_phone_num(self, phone):
        user = await db.query("select user_id, agent_id, current_timestamp from pharmex_front_users_details where phone = $1 or phone2 = $1", (phone,))

        if user is not None:
            return {"user": user}
        else:
            return None
