import os
import shutil
import re
from datetime import datetime


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def build_hash_dict(script_dir):
    """读取hash.txt，构建替换字典"""
    hash_file = os.path.join(script_dir, "hash.txt")
    result = {}
    
    if not os.path.exists(hash_file):
        print(f"警告: {hash_file} 不存在")
        return result
    
    with open(hash_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "to" in line:
                parts = line.partition("to")
                key = parts[0].strip()
                value = parts[2].strip()
                # 空判断：key和value都不能为空
                if key and value:
                    result[key] = value
    
    print(f"已加载 {len(result)} 条替换规则")
    return result


def find_ini_files(script_dir):
    """递归扫描所有不包含DISABLED且以.ini结尾的文件"""
    ini_files = []
    for root, dirs, files in os.walk(script_dir):
        for f in files:
            if f.endswith(".ini") and "DISABLED" not in f:
                ini_files.append(os.path.join(root, f))
    return ini_files


def backup_ini_files(ini_files):
    """备份所有ini文件，命名格式: DISABLED_BACKUP_时间戳_原文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for ini_path in ini_files:
        dir_name = os.path.dirname(ini_path)
        file_name = os.path.basename(ini_path)
        backup_name = f"DISABLED_BACKUP_{timestamp}_{file_name}"
        backup_path = os.path.join(dir_name, backup_name)
        
        shutil.copy2(ini_path, backup_path)
        print(f"已备份: {file_name} -> {backup_name}")


def process_ini_files(ini_files, hash_dict):
    """扫描ini文件，替换hash行中匹配字典key的字符串"""
    if not hash_dict:
        print("字典为空，跳过替换")
        return
    
    for ini_path in ini_files:
        with open(ini_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines:
            # 当一行中包含hash时才处理
            if "hash" in line:
                new_line = line
                for key, value in hash_dict.items():
                    # 使用正则确保完整单词匹配，避免部分匹配
                    pattern = r'\b' + re.escape(key) + r'\b'
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, value, new_line)
                        modified = True
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        if modified:
            with open(ini_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"已修改: {os.path.basename(ini_path)}")


def main():
    script_dir = get_script_dir()
    
    # 1-2. 读取hash.txt构建字典
    hash_dict = build_hash_dict(script_dir)
    
    # 3. 扫描所有符合条件的ini文件
    ini_files = find_ini_files(script_dir)
    print(f"找到 {len(ini_files)} 个ini文件")
    
    if not ini_files:
        print("未找到符合条件的ini文件")
        return
    
    # 4. 备份所有ini文件
    backup_ini_files(ini_files)
    
    # 5. 逐一扫描并替换
    process_ini_files(ini_files, hash_dict)
    
    print("处理完成")
    input("按下任意键以确定...")


if __name__ == "__main__":
    print(f"注意此脚本需要你在同脚本目录下设置hash.txt文件,格式为:  123456 to 234567")
    input("按下任意键以确定...")
    main()
