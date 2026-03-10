
def normalize_path(path: str) -> str:
    """
    :param path: unix path to normalize
    :return: normalized path
    """
    if path == '':
        return '.'
    parts = path.split("/")
    root = False
    if len(parts) >= 1 and parts[0] == "":
        root = True
        parts = parts[1:]
    stack = []
    for part in parts :
        if part == "" or part == ".":
            continue
        elif part == "..":
            if len(stack)>=1 and stack[-1] != "..":
                stack.pop()
            elif root and len(stack) == 0:
                continue
            else:
                stack.append(part)
        else:
            stack.append(part)
    if len(stack) == 0:
        if root:
            return '/'
        return '.' # root moment
    else:
        return ("/" if root else "") +  '/'.join(stack)
