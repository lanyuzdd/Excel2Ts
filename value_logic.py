import json

# 值类型，分基础值类型和业务值类型
sys_base_types = ['string', 'float', 'int', 'comment']
sys_business_types = ['equip_slot', 'item_key_name', 'role_prop']
# 值类型修饰
sys_value_prefixes = ['key', 'primary_key', 'key_value_key', 'key_value_value', 'list']

sys_unique_value_prefixes = ['key', 'primary_key', 'key_value_key']


# 解析表格列的值类型数据，int:equip_slot|key，int:equip_slot|list
def get_column_value_type_data(value_type_str):
    data = {'base_type': '', 'business_type': '', 'prefixes': ''}
    prefixes = value_type_str.split('|')
    value_types = prefixes[0].split('|')
    if len(value_types) >= 2:
        raise TypeError("值类型错误，最多两个：" + json.dumps(value_types))
    base_type = value_types[0]
    if base_type not in sys_base_types:
        raise TypeError("基础值类型错误：" + base_type)
    data['base_type'] = base_type

    if base_type == 'comment':
        return data

    if len(value_types) == 2:
        business_type = value_types[1]
        if business_type not in sys_business_types:
            raise TypeError("业务值类型错误：" + business_type)
        data['business_type'] = business_type
    else:
        data['business_type'] = ''

    prefixes.pop(0)

    if len(prefixes) > 2:
        raise TypeError("数值修饰不可能超过3个：" + json.dumps(prefixes))
    elif len(prefixes) >= 1:

        unique_prefixes_num = 0
        unique_prefixes = []
        for i in range(0, len(prefixes)):
            v_prefix = prefixes[i]
            if v_prefix not in sys_value_prefixes:
                raise TypeError("值类型修饰错误：" + v_prefix)
            if v_prefix not in unique_prefixes:
                unique_prefixes.append(v_prefix)

            if v_prefix in sys_unique_value_prefixes:
                data['key_prefix'] = v_prefix
                unique_prefixes_num += 1

        if len(unique_prefixes) != len(prefixes):
            raise TypeError("有重复的数值修饰：" + json.dumps(prefixes))

        if unique_prefixes_num > 1:
            raise TypeError("有多个唯一的数值修饰：" + json.dumps(prefixes))

        if 'list' in prefixes:
            prefixes.remove('list')
            if prefixes[0] in sys_unique_value_prefixes:
                raise TypeError("同一个数值类型中，list与键修饰冲突：" + json.dumps(prefixes))

        data['prefixes'] = prefixes
    else:
        data['prefixes'] = []
    return data


# 整表数值修饰检验
def check_sheet_column_type_list(sheet_column_type_list):
    # 所有列只能有一个key类型修饰

    # print('check_all_value_types')
    # print(json.dumps(value_types))

    # 非注释列数量
    uncomment_column_num = get_uncomment_column_num_of_sheet(sheet_column_type_list)

    key_prefix_num = 0

    all_prefixes = []

    # print('check_all_value_types')
    # print(json.dumps(value_types))

    for value_type_item in sheet_column_type_list:
        prefixes = value_type_item['prefixes']
        if prefixes is None:
            continue

        for prefix_item in prefixes:
            # print('prefix_item', prefix_item)
            if prefix_item in sys_unique_value_prefixes:
                key_prefix_num += 1
                if key_prefix_num > 1:
                    raise TypeError("一个表所有列只能有一个key类型修饰：" + str(key_prefix_num) + " " + json.dumps(all_prefixes))
            all_prefixes.append(prefix_item)

        # print('all_prefixes', all_prefixes)
        pass

    if 'key_value_key' in all_prefixes or 'key_value_value' in all_prefixes:
        if 'key_value_key' in all_prefixes and 'key_value_value' in all_prefixes and uncomment_column_num == 2:
            pass
        else:
            prefixes_str = json.dumps(all_prefixes)
            raise TypeError("不是严格的键值对两列格式：" + prefixes_str)
    else:
        pass

    return True


# 表格非注释列数量
def get_uncomment_column_num_of_sheet(sheet_column_type_list):
    uncomment_value_type_num = 0
    for value_type in sheet_column_type_list:
        if value_type['base_type'] == 'comment':
            # comment_value_types.append(value_type)
            pass
        else:
            uncomment_value_type_num += 1
    return uncomment_value_type_num


def get_key_prefix_value_type_data(value_type_data_list):
    for value_type_data in value_type_data_list:
        if 'key_prefix' in value_type_data and value_type_data['key_prefix'] in sys_unique_value_prefixes:
            return value_type_data
    return None
