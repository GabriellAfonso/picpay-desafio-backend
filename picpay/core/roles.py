from rolepermissions.roles import AbstractUserRole


class Personal(AbstractUserRole):
    available_permissions = {
        'make_transfer': True,
        'receive_transfer': True,
    }


class Merchant(AbstractUserRole):
    available_permissions = {
        'make_transfer': False,
        'receive_transfer': True,
    }
