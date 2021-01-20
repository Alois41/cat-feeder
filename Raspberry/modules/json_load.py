import json


def find_cat(cat: str, json_dict: dict):
    if json_dict["name"] == cat:
        return json_dict

    if "children" in json_dict.keys():
        for child in json_dict["children"]:
            res = find_cat(cat, child)
            if res:
                return res
    return None


def add_all_cat(arr: list, sub_dict: dict):
    if "children" in sub_dict.keys():
        for child in sub_dict["children"]:
            add_all_cat(arr, child)
    else:
        arr.append(sub_dict["name"])

    pass


if __name__ == '__main__':
    arr = []
    with open('../hierachy.json') as json_file:
        data = json.load(json_file)
        sub_dict = find_cat("mammal, mammalian", data)
        if sub_dict:
            add_all_cat(arr, sub_dict)
            print(arr)
        else:
            print(None)
