
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    names = dict((val, key) for key, val in enums.iteritems())
    enums['names'] = names
    return type('Enum', (), enums)

SupportedTypes = enum('STRING', 'INTEGER', 'CHECKBOX', 'DROPDOWN', 'NUMERIC_BOOL')

def __cast_string(value):
    if value is not None:
        return str(value)

    raise Exception('Unable to cast STRING.  value={0}'.format(value))

def __cast_integer(value):
    try:
        return int(value)
    except Exception:
        raise Exception('Unable to cast INTEGER.  value={0}'.format(value))

def __cast_checkbox(value):
    if value == 'TRUE':
        return 1
    elif value == 'FALSE':
        return 0

    raise Exception('Unable to cast CHECKBOX.  value={0}'.format(value))

def __cast_dropdown(value):
    try:
        return int(value.split(':')[0])
    except Exception:
        raise Exception('Unable to cast DROPDOWN.  value={0}'.format(value))

def __cast_numeric_bool(value):
    result = None
    try:
        result = int(value)
    except Exception:
        pass
    finally:
        if not ((result == 0) or (result == 1)):
            raise Exception('Unable to cast NUMERIC_BOOL.  value={0}'.format(value))

    return result

def normalize(value):
    value = value.strip()
    if not value:
        value = None

    return value

def cast(t, value):
    value = normalize(value)
    if value is None:
        return None

    if t == SupportedTypes.STRING:
        return __cast_string(value)
    elif t == SupportedTypes.INTEGER:
        return __cast_integer(value)
    elif t == SupportedTypes.CHECKBOX:
        return __cast_checkbox(value)
    elif t == SupportedTypes.DROPDOWN:
        return __cast_dropdown(value)
    elif t == SupportedTypes.NUMERIC_BOOL:
        return __cast_numeric_bool(value)
    else:
        raise Exception('Casting failed to recognize the type.'
                        ' type={0}'
                        ' value={1}'.format(
                        t,
                        value))
