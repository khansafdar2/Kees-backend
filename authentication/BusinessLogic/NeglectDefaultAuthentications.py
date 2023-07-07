
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import AllowAny


def neglect_authentication(views_class):
    remove_restrictions = authentication_classes([])\
        (permission_classes([AllowAny])
         (views_class).as_view())
    return remove_restrictions

