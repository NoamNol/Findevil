from collections import Counter


def normalize_params(params_data: list[dict]) -> dict[str, str]:
    '''
    1. Validate parameters value
    2. Remove missing parameters or use default value
    3. Force no more than one parameter in group (For example, only one 'filter' parameter)
    '''
    result = {}
    groups_counter = Counter()

    for p in params_data:
        name = p['name']
        value = p['value']
        to_string = p.get('toString', str)
        group = p.get('group')
        validator = p.get('validator')

        if value is None:
            default = p.get('default')
            if default is not None:
                value = default
            else:
                continue
        if group:
            groups_counter[group] += 1
            if groups_counter[group] > 1:
                raise ValueError(f"Must specify exactly one {group} parameter")
        if validator:
            message, is_valid = validator
            if (not is_valid(value)):
                raise ValueError(f"{name}:{value} is invalid parameter ({message})")

        result[name] = to_string(value)
    return result
