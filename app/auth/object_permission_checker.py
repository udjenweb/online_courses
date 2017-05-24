# coding: utf-8


def checker(fn_list, user, resource, action_type, json):
    """allow if one agreed and the others abstained"""
    from ..resources import get_domains
    domains = get_domains()
    model = domains.get_model(resource)

    for fn, models_list in fn_list:
        if model not in models_list:
            continue

        check_result = fn(user, model, action_type, json)  # + models_list
        assert check_result in [True, False, None]

        if check_result is True:
            return True
        # например мы хотим разрешить назначать роль ученика для учителей
        # при этом модель с ролями может еще и в ACL приложении мониторится

    return False

