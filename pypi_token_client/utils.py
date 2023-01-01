def one_or_none(l):
    if len(l) > 1:
        raise ValueError("more than one element found")
    elif len(l) == 1:
        return l[0]
    return None
