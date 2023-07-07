
from authentication.models import RolePermission, User


def AccessApi(user, access):
    USER = User.objects.get(id=user.id)
    if USER.is_superuser:
        return True
    permission = RolePermission.objects.get(user_id=user.id)

    if permission.vendor and access == "vendor":
        return True
    elif permission.approvals and access == "approvals":
        return True
    elif permission.dashboard and access == "dashboard":
        return True
    elif permission.theme and access == "theme":
        return True
    elif permission.products and access == "products":
        return True
    elif permission.orders and access == "orders":
        return True
    elif permission.customer and access == "customer":
        return True
    elif permission.discounts and access == "discounts":
        return True
    elif permission.configuration and access == "configuration":
        return True
    elif permission.customization and access == "customization":
        return True
    elif permission.notifications and access == "notifications":
        return True
    elif permission.socialfeed and access == "socialfeed":
        return True
    elif permission.blog and access == "blog":
        return True
    return False
