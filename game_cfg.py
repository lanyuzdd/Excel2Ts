import xlwings
import os
import sys
import json
import re
import json2lua
import platform
import workbook_data
from typing import List

file_cfg = None

cur_book_name = None
cur_sheet_name = None
# 当前表格的类型列表
cur_sheet_type_col = None

cur_sheet_column_names = None

# 为了方便复制
# all_tables = ['VIP等级表.xlsx', 'VIP等级特权文字.xlsx', 'VIP系统.xlsx', 'VIP等级奖励', '首充.xlsx',
#               '锻造系统.xlsx', '装备通用.xlsx', '锻造宝石.xlsx',
#               '材料副本.xlsx', '材料副本地图.xlsx',
#               "世界boss.xlsx", '通天塔.xlsx', '世界boss奖励展示.xlsx',
#               '快速获得.xlsx', '快速获得商品.xlsx',
#               '日常活跃.xlsx', '日常活跃任务名索引.xlsx',
#               'test_key.xlsx',
#               'test_key_value.xlsx','学生选课表.xlsx'，'学生选课表key.xlsx',
#               'test_un_primary_key2columns.xlsx']

# 要导出的工作簿文件名
output_tables = ['学生选课表.xlsx']


# 加载配置文件，说明excel路径、导出文件路径
def load_file_cfg():
    global file_cfg
    # print(os.name)
    # print(platform.system())
    sys_name = platform.system()

    file_cfg_path = os.path.join(sys.path[0], 'assets', 'file_cfg.json')

    if sys_name == 'Darwin':
        file_cfg_path = os.path.join(sys.path[0], 'assets', 'file_cfg_mac.json')

    with open(file_cfg_path, 'r', encoding='utf-8') as file:
        file_cfg = json.load(file)

    export_path = file_cfg['export_path']
    if not os.path.exists(export_path):
        print("file_cfg.json配置错误，export_path文件不存在！")
        sys.exit(3)

    for table_item in file_cfg['tables']:
        if not table_item['excel_name'] in output_tables:
            continue

        table_item['path'] = os.path.join(file_cfg["excel_root_path"], table_item['excel_sub_dir'],
                                          table_item['excel_name'])
        print(table_item['path'])
        if not os.path.exists(table_item['path']):
            print('file_cfg.json配置错误，找不到文件:' + table_item['path'])
            sys.exit(2)
        # print(table_item['path'])
        pass


# 加载要导出的excel表文件列表
def load_excel_files():
    for table_item in file_cfg['tables']:
        if not table_item['excel_name'] in output_tables:
            continue
        load_excel_file(table_item)
    pass


# 加载要导出的excel表文件
def load_excel_file(table_item_cfg):
    print("加载工作簿：" + table_item_cfg['excel_name'])

    excel_path = table_item_cfg['path']

    global cur_book_name
    cur_book_name = table_item_cfg['export_name']

    if not workbook_data.is_var_name_ok(cur_book_name):
        print("工作簿的英文名（class_name）非法，请检查配置文件！" + cur_book_name)
        sys.exit(5)

    wb = xlwings.Book(excel_path)
    sheets = wb.sheets
    # print(len(sheets))
    book_json_sheet_data = {}
    book_lua_sheet_data = {}
    workbook = workbook_data.Workbook()
    workbook.name = cur_book_name
    for i in range(0, len(sheets)):
        sheet = sheets[i]
        # print(sheet.name) #Sheet1
        a1_value = sheet.range('A1').value
        print(sheet.name, 'a1', a1_value)
        if a1_value is None:
            continue

        if not workbook_data.is_var_name_ok(sheet.name):
            print("工作簿的表（sheet）名非法，请修改！" + sheet.name)
            sys.exit(6)

        # print('read', sheet.name)

        book_json_sheet_data[sheet.name] = get_sheet_data_template()
        book_lua_sheet_data[sheet.name] = get_sheet_data_template()
        read_sheet(sheet, book_json_sheet_data[sheet.name], book_lua_sheet_data[sheet.name], workbook)
        pass

    ts_define = workbook.get_ts_struct_define()

    tmp_ts_path = os.path.join(sys.path[0], 'assets', 'ts_class', workbook.name + '.ts')
    with open(tmp_ts_path, 'w', encoding='utf-8') as ts_file:
        ts_file.write(ts_define)
        ts_file.close()

    return

    # wb.close()

    # sheet数据去掉map list type结构

    # todo
    # simplified_book_json_data = remove_book_sheet_map_list_type_wrap_and_one_sheet_wrap(book_json_sheet_data)
    # simplified_book_lua_data = remove_book_sheet_map_list_type_wrap_and_one_sheet_wrap(book_lua_sheet_data)

    # todo
    # write_book_data(simplified_book_json_data, simplified_book_lua_data, table_item_cfg)

    # print(json.dumps(simplified_book_json_data))
    # print(json.dumps(simplified_book_lua_data))

    # 没用
    # xlwings.App.kill()
    pass


# 描述表结构的模板
def get_sheet_data_template():
    # primary_key 表含有主键
    # un_primary_key2columns 表不含有主键，共两列值
    # 以上两种情况要去掉值列外面的list封装[]
    temp = {'map': {}, 'list': [], 'type': '', 'primary_key': False, 'un_primary_key2columns': False}
    return temp


# 读取某一张表
# sheet excel sheet对象
# sheet_json_data json的表结构
# sheet_lua_data lua的表结构
def read_sheet(sheet, sheet_json_data, sheet_lua_data, workbook: workbook_data.Workbook):
    print("读取表:" + sheet.name)
    global cur_sheet_name
    cur_sheet_name = sheet.name

    # row_num = sheet.api.UsedRange.Rows.count
    # col_num = sheet.api.UsedRange.Columns.count
    #
    # print('row_num', row_num, 'col_num', col_num)

    #
    rng = sheet.range('A1').expand()
    # 表行数
    row_num = rng.last_cell.row
    # 表列数
    col_num = rng.last_cell.column

    print('row_num', row_num, 'col_num', col_num)

    # 读取表第一行列名
    column_names = sheet.range('A1').expand('right').value
    # 读取表第二行值类型
    column_types = sheet.range('A2').expand('right').value
    # 读取表第三行注释
    column_comments = sheet.range('A3').expand('right').value

    # try:
    wb_sheet = workbook_data.Sheet(cur_sheet_name, column_names, column_types, column_comments)
    # except TypeError as te:
    #     print(str(te.args))
    #     sys.exit(3)
    workbook.sheets.append(wb_sheet)

    workbook.print_sheets_names()

    # return

    # 二维数组，excel读取的原始行列数据

    for row_idx in range(4, row_num + 1):
        # 读取一行
        row_data = sheet.range('A' + str(row_idx)).expand('right').value
        print("row_data origin")
        print(row_data)

        # 数组,原始格式,包括注释列
        row_cell_values = []

        for column_idx in range(0, col_num):
            # 忽略空单元格
            if len(row_data) <= column_idx:
                break

            # 忽略注释单元格
            column_name = column_names[column_idx]
            # if column_name[0:7] == 'comment':
            #     continue

            print('column_idx:', column_idx)
            cell_value = row_data[column_idx]

            column = wb_sheet.column_type_list[column_idx]
            value = column.validate_cell_value_by_column_type(cell_value, row_idx)

            row_cell_values.append(cell_value)
            pass

        wb_sheet.origin_value_rows.append(row_cell_values)

        # print(json.dumps(row_data))

        pass

    print('所有行数据读取完毕')
    pass


# 表所有行数据读取完毕后，按列定义的结构重新组织整表数据结构
def restructure_sheet_json_original_data_with_key(sheet_json_data, row_json_data_list, column_names, key_column_idx):
    sheet_json_data['type'] = 'map'

    for row_json_data_item in row_json_data_list:
        # 表键列名
        key_column_name = column_names[key_column_idx]
        print(key_column_name, json.dumps(row_json_data_item))
        # 拿到行数据中的键值
        key_name = row_json_data_item[key_column_name]
        print(key_name)
        # 删除行数据的键值
        row_json_data_item.pop(key_column_name)
        print('row_json_data_item removed key', json.dumps(row_json_data_item))
        if sheet_json_data['primary_key']:
            if key_name in sheet_json_data['map']:
                raise Exception('primary_key重复!')
            else:
                sheet_json_data['map'][key_name] = row_json_data_item
            pass
        elif sheet_json_data['un_primary_key2columns']:
            if len(row_json_data_item) >= 2:
                raise Exception('un_primary_key2columns判断错误，列数超过3！')

            if key_name not in sheet_json_data['map']:
                sheet_json_data['map'][key_name] = []
            for item_key, item_value in row_json_data_item.items():
                sheet_json_data['map'][key_name].append(item_value)

            pass
        else:
            if key_name not in sheet_json_data['map']:
                sheet_json_data['map'][key_name] = []
            sheet_json_data['map'][key_name].append(row_json_data_item)
        pass
    pass


def restructure_sheet_lua_original_data_with_key(sheet_lua_data, row_lua_data_list, column_names, key_column_idx):
    sheet_lua_data['type'] = 'map'

    for row_lua_data_item in row_lua_data_list:
        key_name = row_lua_data_item[key_column_idx]
        row_lua_data_item.pop(key_column_idx)

        if sheet_lua_data['primary_key']:
            if key_name in sheet_lua_data['map']:
                raise Exception('primary_key重复!')
            else:
                sheet_lua_data['map'][key_name] = row_lua_data_item
            print('restructure_sheet_lua_original_data_with_key primary_key')
            pass
        elif sheet_lua_data['un_primary_key2columns']:
            if len(row_lua_data_item) > 2:
                raise Exception('un_primary_key2columns判断错误，列数超过2！')

            if key_name not in sheet_lua_data['map']:
                sheet_lua_data['map'][key_name] = []
            sheet_lua_data['map'][key_name].append(row_lua_data_item[0])
            print('restructure_sheet_lua_original_data_with_key un_primary_key2columns')

            pass
        else:
            if key_name not in sheet_lua_data['map']:
                sheet_lua_data['map'][key_name] = []

            sheet_lua_data['map'][key_name].append(row_lua_data_item)
            print('restructure_sheet_lua_original_data_with_key common')

        pass
    pass


# todo
def validate_cell_value(value, value_type, column_index):
    res = True

    if value_type == 'number':
        match = re.match(r'^[-+]?[0-9]+\.[0-9]+$', str(value))
        res = match is not None
        return res

    return res


def write_book_data(book_json_sheet_data, book_lua_sheet_data, table_item_cfg):
    # 保存以键值对json
    book_json_sheet_data_path = os.path.join(file_cfg['export_path'] + table_item_cfg['excel_sub_dir'],
                                             table_item_cfg['export_name'] + '.json')
    with open(book_json_sheet_data_path, 'w', encoding='utf-8') as book_json_sheet_data_file:
        json.dump(book_json_sheet_data, fp=book_json_sheet_data_file, sort_keys=True, indent=4,
                  separators=(',', ':'), ensure_ascii=False)
        book_json_sheet_data_file.close()

    no_book_json_sheet_data_path = os.path.join(file_cfg['export_path'] + table_item_cfg['excel_sub_dir'],
                                                table_item_cfg['export_name'] + '_list.json')

    with open(no_book_json_sheet_data_path, 'w', encoding='utf-8') as no_book_json_sheet_data_file:
        json.dump(book_lua_sheet_data, fp=no_book_json_sheet_data_file, sort_keys=True, indent=4, separators=(',', ':'),
                  ensure_ascii=False)
        no_book_json_sheet_data_file.close()

    # kv_lua_path = os.path.join(file_cfg['export_path'] + table_item_cfg['excel_sub_dir'],
    #                            table_item_cfg['export_name'] + '_kv.lua')

    # with open(kv_lua_path, 'w', encoding='utf-8') as kv_lua_file:
    #     content = 'local ' + table_item_cfg['export_name'] + ' = ' + json2lua.dic_to_lua_str(book_json_sheet_data)
    #     kv_lua_file.write(content)
    #     kv_lua_file.close()

    # lua_path = os.path.join(file_cfg['export_path'] + table_item_cfg['excel_sub_dir'],
    #                         table_item_cfg['export_name'] + '.lua')
    #
    # with open(lua_path, 'w', encoding='utf-8') as lua_file:
    #     content = 'local ' + table_item_cfg['export_name'] + ' = ' + json2lua.dic_to_lua_str(book_lua_sheet_data)
    #     lua_file.write(content)
    #     lua_file.close()

    write_book_data_d_ts(book_json_sheet_data, table_item_cfg)

    pass


def write_book_data_d_ts(book_json_sheet_data, table_item_cfg):
    pass


# 验证主键列的所有值是否唯一
def validate_primary_key_column(sheet, column_idx):
    pass


def format_book_sheet_data(book_sheet_data):
    pass


def remove_book_sheet_map_list_type_wrap_and_one_sheet_wrap(book_sheet_data):
    simplified_book_data = {}
    for sheet_name, sheet_data in book_sheet_data.items():
        if sheet_data['type'] == 'list':
            if len(book_sheet_data) == 1:
                simplified_book_data = sheet_data['list']
            else:
                simplified_book_data[sheet_name] = sheet_data['list']
        else:
            if len(book_sheet_data) == 1:
                simplified_book_data = sheet_data['map']
            else:
                simplified_book_data[sheet_name] = sheet_data['map']
    return simplified_book_data


load_file_cfg()
load_excel_files()
