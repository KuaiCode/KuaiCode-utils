# -*- coding: utf-8 -*-
"""
OneTab 数据去重工具

本脚本用于处理从 OneTab 浏览器扩展导出的数据文件。
主要功能是读取文件内容，根据每一行的 URL 地址进行去重，然后将去重后的结果
写回原文件或指定的输出文件。

功能：
- 使用 rich.progress 显示美观的读写进度条。
- 使用 argparse 解析命令行参数，提供友好的用户界面。
- 支持指定输入和输出文件，若不指定输出文件则默认覆盖原文件。

如何使用:
1.  覆盖原文件:
    python onetab_dedupe.py /path/to/your/onetab_export.txt

2.  导出到新文件:
    python onetab_dedupe.py /path/to/your/onetab_export.txt /path/to/new_deduped_file.txt
"""

import argparse
from rich.progress import track

def read_file(file_path: str, encoding="utf-8"):
    """
    从指定路径读取文件，并返回一个包含所有行的列表。

    Args:
        file_path (str): 要读取的文件的路径。
        encoding (str, optional): 文件编码格式。默认为 "utf-8"。

    Returns:
        list: 包含文件中每一行内容的列表。
    """
    data_list = []
    # 使用 with open 确保文件操作后自动关闭
    # rich.track 会自动为文件读取过程添加一个进度条
    with open(file=file_path, mode="r", encoding=encoding) as file:
        for line in track(sequence=file, description="读取文件中..."):
            data_list.append(line)
    return data_list

def deduplicate(data_list: list):
    """
    对包含 OneTab 数据的列表进行去重。

    去重逻辑：
    - OneTab 导出的格式通常为 "URL | 页面标题"。
    - 本函数会提取每行中第一个 '|' 符号前的 URL 部分进行比较。
    - 使用一个集合 (set) 来高效地跟踪已经出现过的 URL。
    - 空行会被保留。

    Args:
        data_list (list): 从文件读取的原始数据列表。

    Returns:
        list: 经过 URL 去重处理后的数据列表。
    """
    url_set = set()  # 用于存储已经见过的 URL，实现高效去重
    output_list = []

    for data in track(sequence=data_list, description="处理中..."):
        # 如果是空行或只包含空白字符的行，则直接保留并跳过后续处理
        if not data.strip():
            output_list.append(data)
            continue

        # 核心逻辑：
        # 1. data.strip() - 移除行首尾的空白
        # 2. .split("|", 1) - 按第一个 "|" 分割成最多两部分，避免页面标题中的"|"影响分割
        # 3. [0] - 获取分割后的第一部分，即 URL
        # 4. .strip() - 再次移除可能存在于 URL 周围的空白
        url = data.strip().split("|", 1)[0].strip()

        # 检查这个 URL 是否已经存在于集合中
        if url in url_set:
            # 如果已存在，则跳过此行，不添加到输出列表
            continue
        else:
            # 如果是新的 URL，则将其添加到集合中，并将原始行添加到输出列表
            url_set.add(url)
            output_list.append(data)

    return output_list

def write_file(data_list: list, file_path: str, encoding="utf-8"):
    """
    将数据列表写入到指定的文件路径。

    注意：写入模式为 'w'，会完全覆盖目标文件。

    Args:
        data_list (list): 要写入文件的数据列表。
        file_path (str): 目标文件的路径。
        encoding (str, optional): 文件编码格式。默认为 "utf-8"。
    """
    # 使用 'w' 模式写入文件，如果文件已存在，会先清空再写入
    with open(file=file_path, mode="w", encoding=encoding) as file:
        file.writelines(data_list)
    print(f"处理完成！去重后的文件已保存至: {file_path}")

def main():
    """
    主函数，负责解析命令行参数并协调整个去重流程。
    """
    # --- 1. 设置命令行参数解析 ---
    parser = argparse.ArgumentParser(
        description="OneTab 数据去重工具",
        formatter_class=argparse.RawTextHelpFormatter # 保持 help 信息中的换行格式
    )
    # 定义必需的位置参数：旧文件路径
    parser.add_argument(
        "old_path",
        help="必需: 需要进行去重的OneTab数据文件"
    )
    # 定义可选的位置参数：新文件路径
    # nargs="?" 表示此参数可以出现 0 次或 1 次，如果未提供则其值为 None
    parser.add_argument(
        "new_path",
        nargs="?",
        help="可选: 去重后文件导出路径, 为空则覆盖原文件"
    )
    args = parser.parse_args()

    # --- 2. 处理文件路径 ---
    old_path = args.old_path
    if args.new_path is None:
        # 如果没有提供新路径，则将新路径设置为旧路径，实现覆盖
        new_path = old_path
        print("提示: 导出路径为空, 将默认覆盖原文件")
    else:
        new_path = args.new_path

    # --- 3. 执行核心流程 ---
    data_list = read_file(old_path)
    output_list = deduplicate(data_list=data_list)
    write_file(data_list=output_list, file_path=new_path)

# --- 脚本入口点 ---
# 当该脚本被直接执行时，__name__ 的值是 "__main__"
# 如果它是被其他脚本导入的，__name__ 的值则是模块名 "onetab_dedupe"
if __name__ == "__main__":
    main()