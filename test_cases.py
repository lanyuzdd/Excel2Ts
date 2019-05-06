import json
import os
import json2lua
import sys
import re


# res = json2lua.dic_to_lua_str(json_data)
# print(res)

def test_json_indent():
    json_data = [
        {
            "recharge_num": 100,
            "vip_level": 1
        },
        {
            "recharge_num": 3000,
            "vip_level": 2
        },
        {
            "recharge_num": 10000,
            "vip_level": 3
        },
        {
            "recharge_num": 30000,
            "vip_level": 4
        },
        {
            "recharge_num": 50000,
            "vip_level": 5
        },
        {
            "recharge_num": 100000,
            "vip_level": 6
        },
        {
            "recharge_num": 300000,
            "vip_level": 7
        },
        {
            "recharge_num": 500000,
            "vip_level": 8
        },
        {
            "recharge_num": 1000000,
            "vip_level": 9
        },
        {
            "recharge_num": 2000000,
            "vip_level": 10
        },
        {
            "recharge_num": 5000000,
            "vip_level": 11
        },
        {
            "recharge_num": 10000000,
            "vip_level": 12
        }
    ]

    file_path = os.path.join(sys.path[0], 'assets', 'test_indent.json')
    print(file_path)
    with open(file_path, 'w', encoding='utf-8') as no_kv_json_file:
        # json.dump(json_data, fp=no_kv_json_file, sort_keys=False, indent=4, ensure_ascii=False)
        # json_str = json.dumps(json_data, sort_keys=False, indent=4, ensure_ascii=False)
        json_str = json.dumps(json_data, ensure_ascii=False)
        # json_str = 'local list = ' + json2lua.dic_to_lua_str(json_data)
        # json_str = re.sub(r',\n(\s*)"', ',"', json_str)
        no_kv_json_file.write(json_str)
        no_kv_json_file.close()

    pass


def test_lua_indent():
    json_data = [
        [
            1,
            100
        ],
        [
            2,
            3000
        ],
        [
            3,
            10000
        ],
        [
            4,
            30000
        ],
        [
            5,
            50000
        ],
        [
            6,
            100000
        ],
        [
            7,
            300000
        ],
        [
            8,
            500000
        ],
        [
            9,
            1000000
        ],
        [
            10,
            2000000
        ],
        [
            11,
            5000000
        ],
        [
            12,
            10000000
        ]
    ]

    file_path = os.path.join(sys.path[0], 'assets', 'test_indent.lua')
    print(file_path)
    with open(file_path, 'w', encoding='utf-8') as no_kv_json_file:
        # json.dump(json_data, fp=no_kv_json_file, sort_keys=False, indent=4, ensure_ascii=False)
        # json_str = json.dumps(json_data, sort_keys=False, indent=4, ensure_ascii=False)
        json_str = 'local list = ' + json2lua.dic_to_lua_str(json_data)
        # json_str = re.sub(r',\n(\s*)"', ',"', json_str)
        no_kv_json_file.write(json_str)
        no_kv_json_file.close()
    pass


def test_print_type():
    boo = True
    print(type(boo))

    num1 = 2
    print(type(num1))

    num3 = 0xff000000000000000000000000000000000000000000000000000000000000
    print(type(num3))

    num4 = 1.0
    print(type(num4))

    map1 = {'test': 1}
    print(type(map1))
    pass


def test_json_to_lua():
    json_data = {
        "k11": "v1",
        "k12": 12,
        "base_list1": [
            "item1",
            "item2",
            3,
            1.4,
            0
        ],
        "base_map1": {
            "k11": "v1",
            "k12": 12,
            "v3": 1,
            "v4": 3.333,
            "v5": 234
        },
        "not_base_list1": [
            "item1",
            "item2",
            3,
            1.4,
            0,
            {
                "k11": "v1",
                "k12": 12,
                "v3": 1,
                "v4": 3.333,
                "v5": 234
            },
            "item3",
            "item4"
        ],
        "not_base_map1": {
            "k11": "v1",
            "k12": 12,
            "v3": 1,
            "v4": 3.333,
            "map_in_map": [
                "item1",
                "item2",
                3,
                1.4,
                0
            ]
        }
    }

    # json_data = {
    #     "k1": "v1",
    #     "k2": "v2"
    # }

    # print(json2lua.is_base_value_list(json_data['items13']))
    # print(json2lua.is_base_value_list(json_data['items15']))
    # print(json2lua.is_value_base_value_map(json_data))
    # print(json2lua.is_value_base_value_map(json_data['map14']))
    # print(json2lua.is_value_base_value_map(json_data['map18']))

    # if json_data:
    #     return

    file_path = os.path.join(sys.path[0], 'assets', 'json2lua.lua')
    print(file_path)
    with open(file_path, 'w', encoding='utf-8') as no_kv_json_file:
        json_str = 'local list = ' + json2lua.dic_to_lua_str(json_data)
        no_kv_json_file.write(json_str)
        no_kv_json_file.close()

    pass


def test_dic():
    d1 = {}
    d2 = {'k1': 'v1', 'k1': 'v1'}
    print(len(d1))
    print(len(d2))
    pass


def json_list2lua():
    json_list = [[0, 1.0], [0.7071067811865476, 0.7071067811865475], [1.0, 0], [0.7071067811865476, -0.7071067811865475], [0, -1.0], [-0.7071067811865475, -0.7071067811865476], [-1.0, 0], [-0.7071067811865477, 0.7071067811865475]]
    print(json2lua.dic_to_lua_str(json_list))


# test_json_indent()
# test_lua_indent()
# test_json_to_lua()
# test_dic()
json_list2lua()
