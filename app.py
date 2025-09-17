import shutil
import sys
import re
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTextEdit, QPushButton, QTabWidget, QMessageBox, QLineEdit)
import os
import io
import tempfile
import atexit
from PyQt5 import QtCore, QtWidgets
import platform

# 修改资源加载部分
if getattr(sys, 'frozen', False):
    # 创建临时目录存放资源
    temp_dir = tempfile.mkdtemp()
    atexit.register(lambda: os.rmtree(temp_dir) if os.path.exists(temp_dir) else None)

    # 设置 Qt 插件路径
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(temp_dir, 'plugins')

    # 创建插件目录
    plugin_subdir = "platforms"
    if platform.system() == "Darwin":
        plugin_subdir = "platforms"

    platforms_dir = os.path.join(temp_dir, plugin_subdir)
    os.makedirs(platforms_dir, exist_ok=True)




    # 获取资源目录路径
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 复制平台插件
    src_plugins_dir = os.path.join(base_path, 'qt_plugins', 'plugins', 'platforms')

    # 根据平台选择插件文件
    if platform.system() == "Windows":
        plugins = ['qwindows.dll']
    elif platform.system() == "Darwin":
        plugins = ['libqcocoa.dylib']
    else:  # Linux
        plugins = ['libqxcb.so']

    for plugin in plugins:
        src_path = os.path.join(src_plugins_dir, plugin)
        if os.path.exists(src_path):
            dest_path = os.path.join(platforms_dir, plugin)
            shutil.copy2(src_path, dest_path)
            print(f"已复制插件: {plugin} -> {dest_path}")
        else:
            print(f"警告: 插件不存在: {src_path}")
class HiveToCKConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hive 到 ClickHouse 转换工具")
        self.setGeometry(100, 100,1200, 1500)

        # 创建主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # 创建转换标签页
        converter_tab = QWidget()
        self.setup_converter_tab(converter_tab)
        tab_widget.addTab(converter_tab, "DDL 转换")

        # 创建 DataX 配置标签页
        datax_tab = QWidget()
        self.setup_datax_tab(datax_tab)
        tab_widget.addTab(datax_tab, "DataX 配置")

    def setup_converter_tab(self, tab):
        layout = QVBoxLayout(tab)

        # 输入部分
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("输入 Hive DDL 建表语句:"))
        self.hive_ddl_input = QTextEdit()
        self.hive_ddl_input.setPlaceholderText("请采用 \n\nshow create table 表 \n\n方式获取hive表的完整建表语句,否则生成内容不全")
        self.hive_ddl_input.setMinimumHeight(150)
        input_layout.addWidget(self.hive_ddl_input)
        layout.addLayout(input_layout)

        # 数据库和表名配置
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("输出数据库名:"))
        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("默认为原库名")
        db_layout.addWidget(self.db_name_input)
        db_layout.addWidget(QLabel("输出表名:"))
        self.table_name_input = QLineEdit()
        self.table_name_input.setPlaceholderText("默认为原表名")
        db_layout.addWidget(self.table_name_input)
        layout.addLayout(db_layout)

        # 转换按钮
        convert_btn = QPushButton("转换")
        convert_btn.clicked.connect(self.convert_ddl)
        layout.addWidget(convert_btn)

        # 输出部分
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("ClickHouse 建表语句:"))
        self.ck_ddl_output = QTextEdit()
        self.ck_ddl_output.setReadOnly(True)
        self.ck_ddl_output.setMinimumHeight(200)
        output_layout.addWidget(self.ck_ddl_output)
        layout.addLayout(output_layout)

    def setup_datax_tab(self, tab):
        layout = QVBoxLayout(tab)

        # DataX 配置部分
        config_layout = QVBoxLayout()
        config_layout.addWidget(QLabel("DataX 配置参数:"))

        # ClickHouse 配置
        ck_layout = QHBoxLayout()
        ck_layout.addWidget(QLabel("ClickHouse JDBC URL:"))
        self.ck_jdbc_input = QLineEdit("jdbc:clickhouse://cc-2ze44up91s10912m1.ads.rds.aliyuncs.com:8123")
        ck_layout.addWidget(self.ck_jdbc_input)
        config_layout.addLayout(ck_layout)

        # 用户名密码
        auth_layout = QHBoxLayout()
        auth_layout.addWidget(QLabel("ClickHouse 用户名:"))
        self.ck_user_input = QLineEdit("data_ck_test")
        auth_layout.addWidget(self.ck_user_input)
        auth_layout.addWidget(QLabel("密码:"))
        self.ck_password_input = QLineEdit("NyT2T0XXuGjyaaapvOg7QNZiQdaCnnzRpKlosTMhL+R+Sa+71vvW85si2G9ygeuMpVhZSuD8T+jHhE+d3vXbuhkqYQ8DeyYVREmYPBTBreE2yI9ze2jNW9B+I6BEvYRqupjK0rWopxi52l5mUO6rIF9uIEzptKL4KdcYgtyKtmo=")
        self.ck_password_input.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.ck_password_input)
        config_layout.addLayout(auth_layout)
        layout.addLayout(config_layout)
        # 生成按钮
        generate_btn = QPushButton("生成 DataX 配置")
        generate_btn.clicked.connect(self.generate_datax_config_1)
        layout.addWidget(generate_btn)

        # 输出部分
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("DataX JSON 配置:"))
        self.datax_output = QTextEdit()
        self.datax_output.setReadOnly(True)
        self.datax_output.setMinimumHeight(300)
        output_layout.addWidget(self.datax_output)
        layout.addLayout(output_layout)

    def parse_hive_ddl(self, ddl_content: str) -> dict:
        """解析 Hive DDL 语句"""
        result = {
            'db_name': '',
            'table_name': '',
            'columns': [],
            'partition_columns': [],
            'comment': '',
            'location': '',
            'storage_format': 'TEXTFILE',
            'file_type': 'text',            # 默认文件类型
            'field_delimiter': '\u0001',    # 默认字段分隔符
        }

        # 提取表名
        table_match = re.search(r'create\s+table\s+(?:if\s+not\s+exists\s+)?`?([\w\.]+)`?',
                                ddl_content, re.IGNORECASE)
        if table_match:
            full_table_name = table_match.group(1)
            # 分离数据库名和表名
            if '.' in full_table_name:
                # 使用非贪婪匹配，只分割第一个点
                parts = full_table_name.split('.', 1)
                result['db_name'] = parts[0]
                result['table_name'] = parts[1]
            else:
                result['table_name'] = full_table_name
        # 提取列信息
        pattern = r'\(\s*((?:[^()]|\(.*?\))*?)\s*\)\s*(?=PARTITIONED\s+BY|ROW\s+FORMAT|STORED\s+AS|LOCATION|TBLPROPERTIES|$)'
        columns_section = re.search(pattern, ddl_content, re.IGNORECASE | re.DOTALL)
        if columns_section:
            columns_text = columns_section.group(1)
            # 匹配列定义
            column_pattern = r'`?(\w+)`?\s+(\w+(?:\(\d+(?:,\d+)?\))?)\s*(?:COMMENT\s*[\'"](.*?)[\'"])?'
            columns = re.findall(column_pattern, columns_text, re.IGNORECASE)

            for col_name, col_type, col_comment in columns:
                # 清理注释
                if col_comment:
                    col_comment = col_comment.strip().strip("'").strip('"')

                # 映射类型
                base_type = re.sub(r'\(.*\)', '', col_type).lower()
                ck_type = self.map_to_ck_type(base_type)

                result['columns'].append({
                    'name': col_name,
                    'type': ck_type,
                    'comment': col_comment or ''
                })

        # 提取分区列
        partition_match = re.search(r'PARTITIONED\s+BY\s*\(([^)]+)\)', ddl_content, re.IGNORECASE)
        if partition_match:
            partition_text = partition_match.group(1)
            # 匹配分区列定义
            partition_pattern = r'`?(\w+)`?\s+(\w+(?:\(\d+(?:,\d+)?\))?)'
            partitions = re.findall(partition_pattern, partition_text, re.IGNORECASE)

            for col_name, col_type in partitions:
                base_type = re.sub(r'\(.*\)', '', col_type).lower()
                ck_type = self.map_to_ck_type(base_type, is_key=True)

                result['partition_columns'].append({
                    'name': col_name,
                    'type': ck_type,
                    'comment': '分区字段'
                })

        # 提取表注释
        comment_match = re.search(r"COMMENT\s*['\"](.*?)['\"]", ddl_content, re.IGNORECASE)
        if comment_match:
            result['comment'] = comment_match.group(1)

        location_match = re.search(r'LOCATION\s*[\'"]([^\'"]+)[\'"]', ddl_content, re.IGNORECASE)
        if location_match:
            result['location'] = location_match.group(1)

            # 转换为小写以简化匹配
        ddl_lower = ddl_content.lower()

        # 提取存储格式
        if 'stored as orc' in ddl_lower:
            result['storage_format'] = 'ORC'
            result['file_type'] = 'orc'
        elif 'stored as parquet' in ddl_lower:
            result['storage_format'] = 'PARQUET'
            result['file_type'] = 'parquet'
        elif 'stored as avro' in ddl_lower:
            result['storage_format'] = 'AVRO'
            result['file_type'] = 'avro'
        elif 'stored as sequencefile' in ddl_lower:
            result['storage_format'] = 'SEQUENCEFILE'
            result['file_type'] = 'sequence'
        elif 'stored as textfile' in ddl_lower:
            result['storage_format'] = 'TEXTFILE'
            result['file_type'] = 'text'

        # 提取行格式和字段分隔符
        row_format_match = re.search(r'row format delimited\s+fields terminated by\s+[\'"]([^\'"]+)[\'"]',
                                     ddl_content, re.IGNORECASE)
        if row_format_match:
            delimiter = row_format_match.group(1)
            # 处理特殊分隔符
            if delimiter == '\\t':
                result['field_delimiter'] = '\t'
            elif delimiter == '\\001':
                result['field_delimiter'] = '\u0001'
            elif delimiter == ',':
                result['field_delimiter'] = ','
            else:
                result['field_delimiter'] = delimiter

        # 提取输入输出格式
        input_format_match = re.search(r'inputformat\s*[\'"]([^\'"]+)[\'"]', ddl_content, re.IGNORECASE)
        output_format_match = re.search(r'outputformat\s*[\'"]([^\'"]+)[\'"]', ddl_content, re.IGNORECASE)

        if input_format_match:
            input_format = input_format_match.group(1).lower()
            if 'orc' in input_format:
                result['storage_format'] = 'ORC'
                result['file_type'] = 'orc'
            elif 'parquet' in input_format:
                result['storage_format'] = 'PARQUET'
                result['file_type'] = 'parquet'
            elif 'avro' in input_format:
                result['storage_format'] = 'AVRO'
                result['file_type'] = 'avro'

        return result

    def map_to_ck_type(self, hive_type: str, is_key: bool = False) -> str:
        """映射 Hive 类型到 ClickHouse 类型
        :param hive_type: Hive 数据类型
        :param is_key: 是否为排序键或分区键字段
        """
        # 基础类型映射
        type_mapping = {
            'int': 'Int32',
            'long': 'Int64',
            'bigint': 'Int64',
            'double': 'Float64',
            'float': 'Float32',
            'string': 'String',
            'varchar': 'String',
            'char': 'String',
            'boolean': 'UInt8',
            'tinyint': 'Int8',
            'smallint': 'Int16',
            'timestamp': 'DateTime',
            'date': 'Date',
            'decimal': 'Decimal(38, 10)'
        }

        # 获取基础类型
        base_type = type_mapping.get(hive_type, 'String')

        # 如果是键字段，直接返回基础类型（非Nullable）
        if is_key:
            return base_type

        # 非键字段添加Nullable修饰
        return f'Nullable({base_type})'
    def generate_ck_ddl(self, db_name: str, table_name: str, table_info: dict) -> str:
        """生成 ClickHouse 建表语句"""
        columns = table_info['columns'] + table_info['partition_columns']

        ddl_lines = [
            f"-- 原始 Hive 表: {table_info['db_name']}.{table_info['table_name']}",
            f"-- 表注释: {table_info['comment']}",
            "",
            f"CREATE TABLE IF NOT EXISTS {db_name}.{table_name}",
            "("
        ]

        # 修改排序键的类型,确定排序键
        order_by_field = self.find_order_by_field(columns)

        # 添加列定义
        column_defs = []
        for col in columns:
            if col['name'] == order_by_field:
                col['type'] = self.map_to_ck_type(col['name'], is_key=True)
            col_def = f"    `{col['name']}` {col['type']}"
            if col['comment']:
                col_def += f" COMMENT '{col['comment']}'"
            column_defs.append(col_def)

        ddl_lines.append(",\n".join(column_defs))
        ddl_lines.append(")")
        ddl_lines.append("ENGINE = MergeTree()")

        # 添加排序键

        if order_by_field:
            ddl_lines.append(f"ORDER BY {order_by_field}")

        # 添加分区键
        if table_info['partition_columns']:
            partition_col = table_info['partition_columns'][0]['name']
            ddl_lines.append(f"PARTITION BY {partition_col}")

        ddl_lines.append("SETTINGS index_granularity = 8192;")

        return "\n".join(ddl_lines)

    def find_order_by_field(self, columns: list) -> str:
        """寻找合适的排序键字段"""
        # 优先选择 id 字段
        for col in columns:
            if col['name'].lower() == 'id':
                return col['name']

        # 其次选择时间字段
        time_fields = ['create_time', 'update_time', 'timestamp', 'date', 'time']
        for col in columns:
            if any(tf in col['name'].lower() for tf in time_fields):
                return col['name']

        # 最后选择第一个字段
        if columns:
            return columns[0]['name']

        return ""

    def generate_datax_config(self, db_name: str, table_name: str, table_info: dict) -> dict:
        """生成 DataX 配置"""
        columns = table_info['columns']
        partition_columns = table_info['partition_columns']
        hdfs_path = table_info['location']
        file_type = table_info.get('file_type', 'text')
        field_delimiter = table_info.get('field_delimiter', '\u0001')

        # 构建 reader 的 column 配置
        reader_columns = []
        for idx, col in enumerate(columns):
            # 映射 DataX 类型
            datax_type = self.map_to_datax_type(col['type'])
            reader_columns.append({
                "index": idx,
                "name": col['name'],
                "type": datax_type
            })

        # 添加分区字段作为常量列
        for partition_col in partition_columns:
            col_name = partition_col['name']
            # 根据分区键名称决定使用日期变量还是路径变量
            if col_name in ['partition_id', 'dt']:
                reader_columns.append({
                    "type": "string",
                    "value": "$[yyyy-MM-dd-1]"
                })
            else:
                reader_columns.append({
                    "type": "string",
                    "value": f"${{{col_name}}}"
                })

        # 构建路径部分 - 支持多个分区键
        path_parts = []
        for partition_col in partition_columns:
            col_name = partition_col['name']
            # 根据分区键名称决定使用通配符还是日期变量
            if col_name in ['partition_id', 'dt']:
                path_parts.append(f"{col_name}=$[yyyy-MM-dd-1]")
            else:
                path_parts.append(f"{col_name}=*")

        # 构建完整路径
        if not path_parts:
            path = f"/user/hive/warehouse/{db_name}.db/{table_name}/*"
        else:
            path = f"/user/hive/warehouse/{db_name}.db/{table_name}/{'/'.join(path_parts)+'/'}*"

        # 构建 writer 的 column 配置
        writer_columns = [col['name'] for col in columns + partition_columns]

        # 构建 preSQL（分区表删除分区）
        # pre_sql = []
        # if partition_columns:
        #     partition_col = partition_columns[0]['name']
        #     pre_sql = [f"ALTER TABLE {db_name}.{table_name} DROP PARTITION '${{{partition_col}}}'"]

        # 构建完整配置
        config = {
            "job": {
                "setting": {
                    "speed": {
                        "channel": 5
                    },
                    "jvm": "-Xms4g -Xmx4g -XX:+UseG1GC",
                    "keyVersion": "v1"
                },
                "content": [
                    {
                        "reader": {
                            "name": "hdfsreader",
                            "parameter": {
                                "defaultFS": "hdfs://hdfs-cluster",
                                "path": f"{path}",
                                "fileType": f"{file_type}",
                                "fieldDelimiter": f"{field_delimiter}",
                                "encoding": "UTF-8",
                                "nullFormat": "\\N",
                                "column": reader_columns,
                                "textReaderConfig": {},
                                "hadoopConfig": {
                                    "dfs.nameservices": "hdfs-cluster",
                                    "dfs.ha.namenodes.hdfs-cluster": "nn1,nn2,nn3",
                                    "dfs.namenode.rpc-address.hdfs-cluster.nn1": "master-1-1:8020",
                                    "dfs.namenode.rpc-address.hdfs-cluster.nn2": "master-1-2:8020",
                                    "dfs.namenode.rpc-address.hdfs-cluster.nn3": "master-1-3:8020",
                                    "dfs.client.failover.proxy.provider.hdfs-cluster": "org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider"
                                }
                            }
                        },
                        "writer": {
                            "name": "clickhousewriter",
                            "parameter": {
                                "username": self.ck_user_input.text(),
                                "*password": self.ck_password_input.text(),
                                "column": writer_columns,
                                "connection": [
                                    {
                                        "jdbcUrl": f"{self.ck_jdbc_input.text()}/{db_name}",
                                        "table": [table_name]
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }

        return config

    def map_to_datax_type(self, ck_type: str) -> str:
        """将 ClickHouse 类型映射到 DataX 类型"""
        if 'Int' in ck_type or 'UInt' in ck_type:
            return "long"
        elif 'Float' in ck_type or 'Double' in ck_type or 'Decimal' in ck_type:
            return "double"
        elif 'Date' in ck_type or 'DateTime' in ck_type:
            return "date"
        elif 'Bool' in ck_type:
            return "boolean"
        else:
            return "string"

    def build_hdfs_path(self, db_name: str, table_name: str, partition_columns: list) -> str:
        """构建 HDFS 路径"""
        base_path = f"/user/hive/warehouse/{db_name}.db/{table_name}"

        if not partition_columns:
            return f"{base_path}/*"

        # 构建分区路径
        partition_paths = []
        for part_col in partition_columns:
            partition_paths.append(f"{part_col['name']}=${{{part_col['name']}}}")

        return f"{base_path}/{'/'.join(partition_paths)}/*"

    def convert_ddl(self):
        """转换 Hive DDL 到 ClickHouse DDL"""
        hive_ddl = self.hive_ddl_input.toPlainText().strip()
        db_name = self.db_name_input.text().strip()
        table_name = self.table_name_input.text().strip()

        if not hive_ddl:
            QMessageBox.warning(self, "输入错误", "请输入 Hive DDL 建表语句")
            return

        try:
            # 解析 Hive DDL
            table_info = self.parse_hive_ddl(hive_ddl)

            # 如果表名未输入，使用解析出的表名
            if not table_name:
                table_name = table_info['table_name']
            else:
                table_info['table_name'] = table_name
            # 如果库名未输入，使用解析出的库名
            if not db_name:
                db_name = table_info['db_name']
            else:
                table_info['db_name'] = db_name

            # 生成 ClickHouse DDL
            ck_ddl = self.generate_ck_ddl(db_name, table_name, table_info)
            self.ck_ddl_output.setPlainText(ck_ddl)

            # 更新表库名输入框
            self.table_name_input.setText(table_name)
            self.db_name_input.setText(db_name)


            QMessageBox.information(self, "转换成功", "Hive DDL 已成功转换为 ClickHouse DDL")
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换失败: {str(e)}")

    def generate_datax_config_1(self):
        """生成 DataX 配置"""
        hive_ddl = self.hive_ddl_input.toPlainText().strip()
        db_name = self.db_name_input.text().strip()
        table_name = self.table_name_input.text().strip()

        if not hive_ddl:
            QMessageBox.warning(self, "输入错误", "请输入 Hive DDL 建表语句")
            return


        try:
            # 解析 Hive DDL
            table_info = self.parse_hive_ddl(hive_ddl)

            # 如果表名未输入，使用解析出的表名
            if not table_name:
                table_name = table_info['table_name']
            else:
                table_info['table_name'] = table_name
            # 如果库名未输入，使用解析出的库名
            if not db_name:
                db_name = table_info['db_name']
            else:
                table_info['db_name'] = db_name

            # 更新表库名输入框
            self.table_name_input.setText(table_name)
            self.db_name_input.setText(db_name)

            # 生成 DataX 配置
            datax_config = self.generate_datax_config(db_name, table_name, table_info)

            # 格式化 JSON
            formatted_json = json.dumps(datax_config, indent=4, ensure_ascii=False)
            self.datax_output.setPlainText(formatted_json)

            QMessageBox.information(self, "生成成功", "DataX JSON 配置已生成")
        except Exception as e:
            QMessageBox.critical(self, "生成错误", f"生成失败: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HiveToCKConverter()
    window.show()
    sys.exit(app.exec_())