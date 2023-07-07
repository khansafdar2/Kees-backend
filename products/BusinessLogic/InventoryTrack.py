from products.models import InventoryHistory


def AddInventoryEvent(variant, user, event, quantity, new_inventory, old_inventory):
    try:
        if not old_inventory:
            adjustment = 0
        else:
            adjustment = new_inventory - quantity
        entry = InventoryHistory.objects.create(
            variant=variant,
            event=event,
            adjusted_by=user.username,
            adjustment=adjustment,
            quantity=new_inventory)
        return entry
    except Exception as e:
        return str(e)
