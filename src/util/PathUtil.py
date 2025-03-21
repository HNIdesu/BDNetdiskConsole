def resolve(rootdir:str,*paths:str)->str:
    result = rootdir
    if not result.endswith("/"):
        result += "/"
    part_list = list()
    for path in paths:
        for part in path.split("/"):
            if part == ".":
                continue
            elif part == "..":
                part_list.pop()
            else:
                part_list.append(part)
    return result + "/".join(part_list)