# Excel转ts json
excel转ts json工具用python实现。[策划请看excel表格式要求。](doc/excel.md)


### 搭建python开发环境：

1. 安装python
2. 安装pip
3. clone http://gitlab.kaiqitech.com/xijun.zheng/excel2ts
4. pip install xlwings


excel文件路径、导出的ts文件路径配置在assets/file_cfg.json（windows）、assets/file_cfg_mac.json（macos）。
### 配置file_cfg.json
```java
{
  "info": "游戏配置excel转ts",
  "export_tables":["学生选课表.xlsx","找茬魔方墙配置表.xlsx"],
  "tables": [
    {
      "excel_path": "excel文件所在文件夹路径",
      "excel_name": "excel文件名",
      "export_name": "excel文件导出的ts文件名",
      "export_path": "导出的ts文件路径"
    },
    {
      "excel_path": "D:\\workspace\\pyws\\game_excel\\test\\",
      "excel_name": "学生选课表.xlsx",
      "export_name": "student_lession",
      "export_path": "D:\\workspace\\pyws\\game_excel\\export\\"
    },
    {
      "excel_path": "D:\\workspace\\pyws\\game_excel\\test\\",
      "excel_name": "找茬魔方墙配置表.xlsx",
      "export_name": "more_fan",
      "export_path": "D:\\workspace\\pyws\\game_excel\\export\\"
    }
  ]
}
```

### 运行工具
game_cfg.py是主入口，调用命令行运行：
```java
python game_cfg.py
```
可自行写成.bat或.sh脚本。

### 导出的ts
导出的ts文件以一个excel工作簿为模块。
