import os
import sys
import json
import json2lua
import platform
import workbook_data

# file_cfg.json读取的json
file_cfg = None

# 当前读取的excel名
cur_book_name = None

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
            print("file_cfg.json配置错误，export_path文件不存在！" + export_path)
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

    # print(len(sheets))
    workbook = workbook_data.Workbook(cur_book_name, excel_path)

    list_json, map_json = workbook.to_json()

    workbook.check_workbook_class_name_diff_from_every_sheet_name()
    ts_define = workbook.get_ts_struct_define(map_json)

    # 工程目录，测试用
    # tmp_ts_path = os.path.join(
    #     sys.path[0], 'assets', 'ts_class', workbook.name + '.ts')
    # 读取file_cfg.json配置的发布目录
    tmp_ts_path = os.path.join(
        table_item_cfg['export_path'], workbook.name + '.ts')
    with open(tmp_ts_path, 'w', encoding='utf-8') as ts_file:
        ts_file.write(ts_define)
        ts_file.close()

    # write_book_data(simplified_book_json_data, simplified_book_lua_data, table_item_cfg)
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
