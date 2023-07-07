from authentication.models import ActivityStream, RolePermission


class SystemLogs:
    def post_logs(self, request, request_by_user, action_performed):
        role_name = "-"
        try:
            if request_by_user:
                if request_by_user.role_permission_id is not None:
                    try:
                        role_permission = RolePermission.objects.get(id=request_by_user.role_permission_id)
                        role_name = role_permission.name
                    except Exception as e:
                        print(e)
                        role_name = "-"
        except Exception as e:
            print(e)
            role_name = "-"
        previous_data = "-"
        updated_data = "-"
        if request_by_user:
            username = request_by_user.username
            first_name = request_by_user.first_name
            last_name = request_by_user.last_name
            email = request_by_user.email
        else:
            username = "-"
            first_name = "-"
            last_name = "-"
            email = "-"

        ip_address = get_client_ip(request)
        ActivityStream.objects.create(username=username, role_name=role_name, first_name=first_name,
                                      last_name=last_name,
                                      email=email,
                                      action_performed=action_performed,
                                      previous_data=previous_data,
                                      updated_data=updated_data,
                                      ip_address=ip_address)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
