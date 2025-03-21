def resolve(rootdir:str,*paths:str)->str:
    result = rootdir.strip("/")
    if result != "":
        part_list = result.split("/")
    else:
        part_list = list()
    for path in paths:
        for part in path.split("/"):
            if part == ".":
                continue
            elif part == ".." and part_list:
                part_list.pop()
            else:
                part_list.append(part)
    return "/" + "/".join(part_list)