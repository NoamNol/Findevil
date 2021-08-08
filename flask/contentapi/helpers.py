from collections import Counter


def normalize_params(params_data: list[dict]) -> dict[str, str]:
    '''
    1. Remove missing parameters or use default value
    2. Force no more than one parameter in group (For example, only one 'filter' parameter)
    3. Fix value with a middleware function
    4. Validate parameters value
    5. Convert value to string with simple str(value), or with custom toString function
    '''
    result = {}
    groups_counter = Counter()

    for p in params_data:
        name = p['name']
        value = p['value']
        group = p.get('group')
        middleware = p.get('middleware')
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
        if middleware:
            value = middleware(value)
        if validator:
            message, is_valid = validator
            if (not is_valid(value)):
                raise ValueError(f"{name}:{value} is invalid parameter ({message})")

        to_string = p.get('toString', str)
        result[name] = to_string(value)
    return result
