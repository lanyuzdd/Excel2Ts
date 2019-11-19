# Excel转ts json
excel转ts json工具用python实现。

需要安装excel。

[excel表格式要求。](doc/excel.md)


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
      "excel_path": "D:\\workspace\\pyws\\GameCfg\\assets\\excel\\",
      "excel_name": "学生选课表.xlsx",
      "export_name": "student_lession",
      "export_path": "D:\\workspace\\pyws\\GameCfg\\assets\\ts_class\\"
    },
    {
      "excel_path": "D:\\workspace\\pyws\\GameCfg\\assets\\excel\\",
      "excel_name": "学生选课表key.xlsx",
      "export_name": "student_lession_key",
      "export_path": "D:\\workspace\\pyws\\GameCfg\\assets\\ts_class\\"
    }
  ]
}
```
把file_cfg.json中 **D:\\workspace\\pyws\\** 替换成你的代码仓库本地路径，可以运行仓库自带两个示例学生选课表、学生选课表key。

### 运行工具
game_cfg.py是主入口，调用命令行运行：
```java
python game_cfg.py
```
可自行写成.bat或.sh脚本。

### 导出的ts
导出的ts文件声明了一个模块，对应一个excel工作簿的内容。学生选课表导出的ts文件如下：

```javascript
export namespace student_lession_ns {

    export const popular_teacher_of_year: string = '苍老师';
    export const national_scholarship_money: number = 10000.0;
    export const university_fees: number = 5500.0;
    export interface student_lession {
        student: { [key: string]: student };
        lession: { [key: string]: lession };
        stu_and_lesn: Array<stu_and_lesn>;
        stu_lesn: { [key: string]: Array<stu_lesn> };
        lesn_stu: { [key: string]: Array<lesn_stu> };
    }
    export interface student {
        /** 学生姓名 **/
        name: string;
        /** 年龄 **/
        age: number;
    }
    export interface lession {
        /** 学分 **/
        score: number;
        /** 主讲老师 **/
        teacher: string;
    }
    export interface stu_and_lesn {
        /** 学号 **/
        id: number;
        /** 学生姓名 **/
        name: string;
        /** 课程 **/
        lession: string;
    }
    export interface stu_lesn {
        /** 学号 **/
        id: number;
        /** 课程 **/
        lession: string;
    }
    export interface lesn_stu {
        /** 学生姓名 **/
        name: string;
        /** 学号 **/
        id: number;
    }

    export const json_data: any = {
        "common": {
            "national_scholarship_money": 10000.0,
            "popular_teacher_of_year": "苍老师",
            "university_fees": 5500.0
        },
        "lesn_stu": {
            "体育交谊舞": [
                {
                    "id": 1,
                    "name": "小明"
                },
                {
                    "id": 2,
                    "name": "李雷"
                }
            ],
            "大学物理": [
                {
                    "id": 3,
                    "name": "韩梅梅"
                },
                {
                    "id": 3,
                    "name": "韩梅梅"
                }
            ],
            "微积分": [
                {
                    "id": 1,
                    "name": "小明"
                }
            ],
            "高等代数": [
                {
                    "id": 1,
                    "name": "小明"
                }
            ]
        },
        "lession": {
            "体育交谊舞": {
                "score": 2,
                "teacher": "苍老师"
            },
            "大学物理": {
                "score": 4,
                "teacher": "陈老师"
            },
            "微积分": {
                "score": 4,
                "teacher": "李老师"
            },
            "高等代数": {
                "score": 6,
                "teacher": "王老师"
            }
        },
        "stu_and_lesn": [
            {
                "id": 1,
                "lession": "高等代数",
                "name": "小明"
            },
            {
                "id": 1,
                "lession": "体育交谊舞",
                "name": "小明"
            },
            {
                "id": 1,
                "lession": "微积分",
                "name": "小明"
            },
            {
                "id": 2,
                "lession": "体育交谊舞",
                "name": "李雷"
            },
            {
                "id": 3,
                "lession": "大学物理",
                "name": "韩梅梅"
            },
            {
                "id": 3,
                "lession": "大学物理",
                "name": "韩梅梅"
            }
        ],
        "stu_lesn": {
            "小明": [
                {
                    "id": 1,
                    "lession": "高等代数"
                },
                {
                    "id": 1,
                    "lession": "体育交谊舞"
                },
                {
                    "id": 1,
                    "lession": "微积分"
                }
            ],
            "李雷": [
                {
                    "id": 2,
                    "lession": "体育交谊舞"
                }
            ],
            "韩梅梅": [
                {
                    "id": 3,
                    "lession": "大学物理"
                },
                {
                    "id": 3,
                    "lession": "大学物理"
                }
            ]
        },
        "student": {
            "1": {
                "age": 19,
                "name": "小明"
            },
            "2": {
                "age": 18,
                "name": "李雷"
            },
            "3": {
                "age": 20,
                "name": "韩梅梅"
            },
            "4": {
                "age": 18,
                "name": "小王"
            }
        }
    };
    export const instance: student_lession = json_data;
}

```
代码中使用excel导出的数据和数据结构：
```javascript
console.log(student_lession_ns.student_lession);
```
