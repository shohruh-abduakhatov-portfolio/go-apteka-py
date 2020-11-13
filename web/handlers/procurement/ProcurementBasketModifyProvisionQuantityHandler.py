# region import
from web.handlers.BaseHandler import *
from modules.pharmex.provision.ProvisionExecutorClient_ph import ProvisionExecutorClient_ph
from modules.pharmex.utils.exception_handler import *
# endregion


class ProcurementBasketModifyProvisionQuantityHandler(BaseHandler):

    @throws_handler()
    @allowedRole(Role.PHARMA_CLIENT)
    async def post(self):

        provision_id = int(self.get_argument("provision_id", default=None))
        quantity = int(self.get_argument("quantity", default=0))
        old_quantity = int(self.get_argument("old_quantity", default=0))

        print(provision_id, quantity, old_quantity)

        provision_client = ProvisionExecutorClient_ph()

        response = await provision_client.modify_quantity(data={
            "provision_id": provision_id,
            "quantity": quantity
        })

        """

        response = None
        """
        if response == 'OK':
            self.write({"status": "success"})
        else:
            self.write({"status": response})

        self.finish()
