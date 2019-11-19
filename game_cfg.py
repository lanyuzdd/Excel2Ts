import xlwings
import os
import sys
import json
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

# 要导出的工作簿文件名
output_tables = []


# 加载配置文件，说明excel路径、导出文件路径
def load_file_cfg():
    global file_cfg
    # print(os.name)
    # print(platform.system())
    sys_name = platform.system()

    file_cfg_path = os.path.join(sys.path[0], 'assets', 'file_cfg.json')

    if sys_name == 'Darwin':
        file_cfg_path = os.path.join(
            sys.path[0], 'assets', 'file_cfg_mac.json')

    with open(file_cfg_path, 'r', encoding='utf-8') as file:
        file_cfg = json.load(file)

    global output_tables
    output_tables = file_cfg['export_tables']

    for table_item in file_cfg['tables']:
        if not table_item['excel_name'] in output_tables:
            continue

        export_path = table_item['export_path']
        if not os.path.exists(export_path):
            print("file_cfg.json配置错误，export_path文件不存在！"+export_path)
            sys.exit(3)

        table_item['path'] = os.path.join(
            table_item["excel_path"], table_item['excel_name'])
        print(table_item['path'])
        if not os.path.exists(table_item['path']):
            print('file_cfg.json配置错误，找不到文件:' + table_item['path'])
            sys.exit(2)
        # print(table_item['path'])
        pass


# 加载要导出的excel表文件列表
def load_excel_files():
    tables = []
    for table_item in file_cfg['tables']:
        if not table_item['excel_name'] in output_tables:
            continue
        tables.append(table_item)
    if len(tables) == 0:
        print("请在file_cfg.json配置export_tables要转换的excel文件！")
        sys.exit(3)
    for table_item in tables:
        load_excel_file(table_item)
    pass


# 加载要导出的excel表文件
# table_item_cfg file_cfg.json的table_item
# table_item_cfg.path=table_item_cfg.excel_path+table_item_cfg.excel_name
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
    workbook = workbook_data.Workbook()
    workbook.name = cur_book_name
    for i in range(0, len(sheets)):
        sheet = sheets[i]
        # print(sheet.name) #Sheet1
        a1_value = sheet.range('A1').value
        # print(sheet.name, 'a1', a1_value)
        if a1_value is None:
            continue

        if not workbook_data.is_var_name_ok(sheet.name):
            print("工作簿的表（sheet）名非法，请修改！" + sheet.name)
            sys.exit(6)

        # print('read', sheet.name)

        read_sheet(sheet, workbook)
        pass

    list_json, map_json = workbook.to_json()

    workbook.check_workbook_class_name_diff_from_every_sheet_name()
    ts_define = workbook.get_ts_struct_define(map_json)

    # 工程目录，测试用
    tmp_ts_path = os.path.join(
        sys.path[0], 'assets', 'ts_class', workbook.name + '.ts')
    # 读取file_cfg.json配置的发布目录
    tmp_ts_path = os.path.join(
        table_item_cfg['export_path'], workbook.name + '.ts')
    with open(tmp_ts_path, 'w', encoding='utf-8') as ts_file:
        ts_file.write(ts_define)
        ts_file.close()

    # wb.close()

    # write_book_data(simplified_book_json_data, simplified_book_lua_data, table_item_cfg)

    # 没用
    # xlwings.App.kill()
    pass


# 描述表结构的模板
def get_sheet_data_template():
    # primary_key 表含有主键
    # un_primary_key2columns 表不含有主键，共两列值
    # 以上两种情况要去掉值列外面的list封装[]
    temp = {'map': {}, 'list': [], 'type': '',
            'primary_key': False, 'un_primary_key2columns': False}
    return temp


# 读取某一张表
# sheet excel sheet对象
# sheet_json_data json的表结构
# sheet_lua_data lua的表结构
def read_sheet(sheet, workbook: workbook_data.Workbook):
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
    wb_sheet = workbook_data.Sheet(
        cur_sheet_name, column_names, column_types, column_comments)
    # except TypeError as te:
    #     print(str(te.args))
    #     sys.exit(3)
    workbook.sheets.append(wb_sheet)

    workbook.print_sheets_names()

    # 二维数组，excel读取的原始行列数据

    define_col_num = len(wb_sheet.column_type_list)

    for row_idx in range(4, row_num + 1):
        # 读取一行
        right_cell = chr(ord('A') + len(wb_sheet.column_type_list))
        # print("right_cell char " + right_cell)
        # print(right_cell + str(row_idx))

        # row_data = sheet.range('A' + str(row_idx)).expand('right').value
        # row_data = sheet.range('A', right_cell + str(row_idx)).value
        range_str = 'A' + str(row_idx) + ':' + right_cell + str(row_idx)
        # print("range_str", range_str)
        row_data = sheet.range(range_str).value

        # print("row_data origin")
        # print(row_data)

        # 当前行的实际长度
        cur_row_col_num = len(row_data)

        # 数组,原始格式,包括注释列
        row_cell_values = []

        for column_idx in range(0, define_col_num):
            # print('column_idx:', column_idx)
            if column_idx >= cur_row_col_num:
                cell_value = None
            else:
                cell_value = row_data[column_idx]

            column = wb_sheet.column_type_list[column_idx]
            formatted_value = column.validate_cell_value_by_column_type(
                cell_value, row_idx)

            row_cell_values.append(formatted_value)
            pass

        wb_sheet.origin_value_rows.append(row_cell_values)

        # print(json.dumps(row_data))

        pass

    print('所有行数据读取完毕')
    pass


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

    pass


load_file_cfg()
load_excel_files()
