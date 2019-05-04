import json
import types


# def space_str(layer):
#     lua_str = ""
#     if layer > -1:
#         return lua_str
#     for i in range(0, layer):
#         lua_str += '\t'
#     return lua_str


# def space_str_origin(layer):
#     lua_str = ""
#     for i in range(0, layer):
#         lua_str += '\t'
#     return lua_str


def get_tab_str(tab_num, node=''):
    tab_str = ''
    for i in range(0, tab_num):
        tab_str += '\t'
    # return tab_str + node
    return tab_str


def dic_to_lua_str(data, layer=0, tab_num=0, node='root'):
    # print('layer', layer, 'tab_num', tab_num)

    if type(data) is str:
        return "'" + data + "'"
    if type(data) is bool:
        if data:
            return 'true'
        else:
            return 'false'
    if type(data) in (int, float):
        return str(data)
    if type(data) is list:
        is_base_list = is_base_value_list(data)

        child_tab_num = 0
        if not is_base_list or layer == 0:
            child_tab_num = tab_num + 1

        lua_str = ''

        lua_str += "{"
        for i in range(0, len(data)):

            if layer == 0 or not is_base_list:
                lua_str += '\n'
                lua_str += get_tab_str(child_tab_num, node)
            # list转table加数字下标
            # lua_str += '[' + str(i + 1) + '] = ' + dic_to_lua_str(data[i], layer + 1, child_tab_num, node + "_" + str(i))
            lua_str += dic_to_lua_str(data[i], layer + 1, child_tab_num, node + "_" + str(i))

            if i < len(data) - 1:
                lua_str += ', '

        if not is_base_list:
            lua_str += '\n'
            lua_str += get_tab_str(tab_num)

        lua_str += '}'

        return lua_str
    if type(data) is dict:

        lua_str = "{"

        data_len = len(data)
        data_count = 0

        is_base_value_map = is_value_base_value_map(data)
        child_tab_num = 0
        if not is_base_value_map or layer == 0:
            child_tab_num = tab_num + 1

        for k, v in data.items():

            if layer == 0 or not is_base_value_map:
                lua_str += '\n'

            data_count += 1
            if layer == 0 or not is_base_value_map:
                lua_str += get_tab_str(child_tab_num)

            if type(k) is int:
                lua_str += '[' + str(k) + ']'
            else:
                lua_str += str(k)
            lua_str += ' = '
            try:
                lua_str += dic_to_lua_str(v, layer + 1, child_tab_num, node + '_' + str(k))
                if data_count < data_len:
                    lua_str += ', '
            except Exception:
                print('error in ', k, v)
                raise

        if layer == 0 or not is_base_value_map:
            lua_str += '\n'

        if not is_base_value_map and layer > 0:
            lua_str += get_tab_str(tab_num)

        lua_str += '}'
        return lua_str
    else:
        print(data, 'is error')
        return None


def is_base_value_list(list_item):
    res = type(list_item) is list
    if not res:
        return res

    for item in list_item:
        res = type(item) in (str, int, float)
        if not res:
            return res

    res = True
    return res


def is_value_base_value_map(map_item):
    res = type(map_item) is dict
    if not res:
        return res

    # print(json.dumps(map_item))

    for value in map_item.values():
        res = type(value) in (str, int, float)
        if not res:
            return res

    res = True
    return res
