import os  # NOQA: E402
import sys  # NOQA: E402
import uvloop  # NOQA: E402
uvloop.install()  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'


async def manual_uploader():
    agent = await PharmexSellerExecutorClient().get_user_by_email(email=email)
    await data_clerk.add(supplier_id=agent["agent_id"], key=result["key"], url=result["url"], filename=filename)
