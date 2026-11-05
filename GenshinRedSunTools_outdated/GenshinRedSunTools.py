import os
import shutil
import tkinter
from tkinter import filedialog
from pathlib import Path

def Merage(packname, testrun):
    root_dir='.'
    packTotal = {}
    shouldNum = {}
    Hash = {}
    isHaveHash = True
    for dirpath, dirnames, files_ in os.walk(root_dir, topdown=True):
        # 计算当前目录的深度（root_dir为深度0）
        current_depth = dirpath[len(root_dir):].count(os.sep)
        if current_depth == 1:
            PackName_dir = dirpath.split(os.sep)[1]
            packTotal[PackName_dir] = len(dirnames)
            shouldNum[PackName_dir] = 0
        if current_depth < 2:
            for file_ in files_:
                old_path = os.path.join(dirpath, file_)
                filename, fileext = os.path.splitext(file_)
                new_path = os.path.join(dirpath,"DISABLED_Backup_" + filename + ".txt")
                if "DISABLED_Backup" not in filename and fileext.lower() == ".ini":
                    if not testrun:
                        try:
                            os.replace(old_path, new_path)
                        except Exception as e:
                            print(f"❌ 处理多余ini文件失败: {str(e)}")
                    else:
                        print(f"  模拟备份成功：{old_path}->{new_path}\n")
        if current_depth == 2:
            for file_ in files_:
                if isBlackList(file_) and file_.lower().endswith('.ini'):
                    BaseIni_path = os.path.join(dirpath, file_)
                    filename, fileext = os.path.splitext(file_)
                    BackupIni_path = os.path.join(dirpath,"DISABLED_Backup_" + filename + ".txt")
                    if isHaveHash:
                        Hash = findHash(BaseIni_path)
                        if (len(Hash) != 0):
                            isHaveHash = False
                    if not os.path.exists(BackupIni_path):
                        if not testrun:
                            try:
                                shutil.copy(BaseIni_path, BackupIni_path)
                            except Exception as e:
                                print(f"❌ 备份失败：{str(e)}")
                        else:
                            print(f"  模拟备份成功：{BaseIni_path}->{BackupIni_path}\n")
                    else:
                        print(f"存在备份项目,已跳过: {BackupIni_path}")
                    PackName_dir = BaseIni_path.split(os.sep)[1]
                    modifyIni(BaseIni_path, shouldNum[PackName_dir] , testrun , PackName_dir , packname)
                    shouldNum[PackName_dir] = shouldNum[PackName_dir] + 1
            del dirnames[:]  # 清空子目录列表以阻止进一步遍历
            continue
    packTotal["BaseRootPackName"] = packname
    createRootIni(packTotal , Hash)


def isBlackList(file_):
    blacklist = ["DISABLED", "help", "README"]
    for item in blacklist:
        if item in file_:
            return False
    return True


def findHash(full_path):
    Hash = {}
    key = ""
    with open(full_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line.startswith("[") and line.endswith("Position]"):
            key = "Position"
        elif line.startswith("[") and line.endswith("Blend]"):
            key = "Blend"
        elif line.startswith("[") and line.endswith("Texcoord]"):
            key = "Texcoord"
        elif line.startswith("[") and "VertexLimitRaise" in line:
            key = line
        elif line.startswith("[") and line.endswith("IB]"):
            key = "IB"
        elif line.startswith("[") and line.endswith("Head]"):
            key = "Head"
        elif line.startswith("[") and line.endswith("Body]"):
            key = "Body"
        elif line.startswith("[") and line.endswith("Dress]"):
            key = "Dress"
        elif line.startswith("[") and line.endswith("FaceHeadDiffuse]"):
            key = "FaceHeadDiffuse"
        if key is not None and key != "" and "=" in line:
            if line.startswith("hash") or line.startswith("match_first_index"):
                if key in Hash and Hash[key] is not None and Hash[key] != "":
                    Hash[key] = Hash[key] + "\n" + line
                else:
                    Hash[key] = line
            elif line.startswith(";;hash") or line.startswith(";;match_first_index"):
                if key in Hash and Hash[key] is not None and Hash[key] != "":
                    Hash[key] = Hash[key] + "\n" + line[2:]
                else:
                    Hash[key] = line[2:]
    return Hash

def createRootIni(packNameAndNum , Hash):
    lines_key = []
    lines_value = []
    for key, value in packNameAndNum.items():
        if key != "BaseRootPackName":
            lines_key.append(key)
            lines_value.append(value)
    lines_text = [] 
    lines_text.append("; namespace ------------------------- \nnamespace = " + packNameAndNum["BaseRootPackName"] + "\n\n; Constants -------------------------\n[Constants]\n\n;_2 Variables -------------------------")
    for key in lines_key:
        lines_text.append("\nglobal persist $" + key + " = 0")
    lines_text.append("\nglobal persist $modpack = 0\nglobal $active\n\n;_2 Key -------------------------\n[KeyModUP]\ncondition = $active == 1\nkey = ALT VK_UP\ntype = hold\nrun = CommandListPackUp\n\n[KeyModDOWN]\ncondition = $active == 1\nkey = ALT VK_DOWN\ntype = hold\nrun = CommandListPackDown\n\n[KeyPack]\ncondition = $active == 1\nkey = VK_OEM_3 VK_UP\nback = VK_OEM_3 VK_DOWN\ntype = cycle\n$modpack = ")
    i = 0
    str_ = ""
    for key in lines_key:
        if i == 0:
            str_ = "0"
        else:
            str_ = str_ + "," + str(i)
        i +=1
    lines_text.append(str_ + "\nrun = CommandListPack \n\n;_2 Present -------------------------\n[Present]\npost $active=0")
    i = 0
    for key in lines_key:
        int_num = int(lines_value[i]) - 1
        if int_num < 0:
            num = "0"
        else:
            num = str(int_num)
        lines_text.append("\n\nif $"+key+" < 0 \n\t$"+key+" = "+num+"\nelif $"+key+" > "+num+"\n\t$"+key+" = 0"+"\nendif")
        i = i + 1
    lines_text.append("\n\n; CommandList -------------------------\n[CommandListPackUp]\n")
    i = 0
    for key in lines_key:
        if i == 0:
            lines_text.append("if $modpack == "+str(i)+"\n\t$"+key+" = $"+key +" + 1")
        else:
            lines_text.append("\nelif $modpack == "+str(i)+"\n\t$"+key+" = $"+key +" + 1")
        i +=1
    lines_text.append("\nendif\n\n[CommandListPackDown]\n")
    i = 0
    for key in lines_key:
        if i == 0:
            lines_text.append("if $modpack == "+str(i)+"\n\t$"+key+" = $"+key +" - 1")
        else:
            lines_text.append("\nelif $modpack == "+str(i)+"\n\t$"+key+" = $"+key +" - 1")
        i +=1
    lines_text.append("\nendif\n\n[CommandListPack]\n")
    i = 0
    for key in lines_key:
        if i == 0:
            lines_text.append("if $modpack == "+str(i)+"\n\tpost Resource\\ShaderFixes\\help.ini\\Notification = ResourcePack."+str(i))
        else:
            lines_text.append("\nelif $modpack == "+str(i)+"\n\tpost Resource\\ShaderFixes\\help.ini\\Notification = ResourcePack."+str(i))
        i +=1
    lines_text.append("\nendif\npost run = CustomShader\\ShaderFixes\\help.ini\\FormatText\npost $\\ShaderFixes\\help.ini\\notification_timeout = time + 5.0\n\n; Resource -------------------------")
    i = 0
    for key in lines_key:
        lines_text.append("\n[ResourcePack."+str(i)+"]\ntype = Buffer\ndata = \""+key+"\"\n")
        i +=1
    lines_text.append("\n; Override -------------------------")
    if len(Hash) == 0:
        print("警告：无示例Hash，合并生成终止。")
        exit(0)
    for key, value in Hash.items():
        i = 0
        if "VertexLimitRaise" not in key:
            lines_text.append("\n[TextureOverride"+packNameAndNum["BaseRootPackName"]+key+"]\n" + value)
            if "Position" == key:
                lines_text.append("\n$active = 1 ")
            tempstr = "\nif $modpack == 0"
            for keys in lines_key:
                if i > 0:
                    tempstr = tempstr + "\nelif $modpack == "+str(i)
                int_num = int(lines_value[i]) - 1
                if int_num < 0:
                    int_num = 0
                n = 0
                tempstr = tempstr + "\n\tif $"+keys+" == " + str(n) + "\n\t\trun = commandlist\\"+packNameAndNum["BaseRootPackName"]+keys+"\\pack"+str(n)+"\\"+packNameAndNum["BaseRootPackName"]+key.lower()
                while n <= int_num:
                    if n > 0:
                        tempstr = tempstr + "\n\telif $"+keys+" == " + str(n) + "\n\t\trun = commandlist\\"+packNameAndNum["BaseRootPackName"]+keys+"\\pack"+str(n)+"\\"+packNameAndNum["BaseRootPackName"]+key.lower()
                    n +=1
                tempstr = tempstr + "\n\tendif"
                i +=1
            lines_text.append(tempstr + "\nendif\n")
        else:
            lines_text.append("\n"+key + "\n" +value + "\n")
    lines_text.append("\n; ShaderOverride -------------------------\n")

    # 创建新文件（若存在则覆盖）
    with open(".\\"+packNameAndNum["BaseRootPackName"]+".ini", "w", encoding="utf-8") as f:
        f.writelines(lines_text)

def modifyIni_NoNeedNote(line):
    line = line.strip()
    NoNeedS = ["namespace"]
    if line[0] != ';':
        for NoNeed in NoNeedS:
            if NoNeed in line:
                return True
    elif line[0] == ';':
        if ";;" not in line and "--" in line:
            NoteTextS = ["namespace","Overrides","CommandList","Resource"]
            for NoteText in NoteTextS:
                if NoteText in line:
                    return True
    return False


def modifyIni(filename , isNum , testrun , spacename , packname):
    isCollect = 0
    isResource = 0
    isMoreNull = 0
    new_lines = []
    Resource_lines = []
    attribute = {}
    key = ""
    # 读取文件内容到列表
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    new_lines.insert(0, "; namespace ------------------------- \nnamespace = " + packname + spacename + "\\Pack" +str(isNum) +"\n")
    DefaultName = ""
    for line in lines:
        if line.strip().lower() == "":
            isMoreNull +=1
        else:
            isMoreNull = 0
            if modifyIni_NoNeedNote(line):
                continue
        if isMoreNull > 2 and line.lower() == "":
            continue
        no_annotation_line = line.split(';')[0].strip()
        if no_annotation_line.startswith("hash") or no_annotation_line.startswith("match_first_index"):
            line = ";;" + line
        if no_annotation_line.startswith("[TextureOverride") or no_annotation_line.startswith("[CommandList"):
            if DefaultName is not None or DefaultName == "":
                DefaultName = line.replace("[TextureOverride","").replace("Position]","")
            key = line.replace("[TextureOverride", "[CommandList").strip()
            isCollect = 1
            continue
        elif no_annotation_line.startswith("[") and no_annotation_line.endswith("]"):
            isCollect = 0
        if isCollect == 1:
            if no_annotation_line.startswith("run") and "=" in no_annotation_line and key.replace("[","").replace("]","") in no_annotation_line:
                # continue
                line = ";" + line
            if key in attribute and attribute[key] is not None and attribute[key] != "":
                attribute[key] = attribute[key] + line
            else:
                attribute[key] = line
        elif isCollect == 0:
            if no_annotation_line.startswith("[Resource"):
                isResource = 1
            elif no_annotation_line.startswith("[") and not no_annotation_line.startswith("[Resource"):
                isResource = 0
            if isResource == 1:
                Resource_lines.append(line)
            else:
                new_lines.append(line)
    new_lines.append("\n; Overrides ------------------------- \n\n; CommandList ------------------------- \n")
    for key, value in attribute.items():
        # if "[CommandList" in key and isFrist:
        #     value
        if "Position" in key and "$active" not in value:
            value = "$active = 1\n" + value
        new_lines.append(key.replace(DefaultName, packname) + "\n" + value)
    new_lines.append("\n ; Resource ------------------------- \n")
    new_lines = new_lines + Resource_lines
    if not testrun:
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        print("文件修改完成。")
    else:
        print("测试模拟: 假设ini内容已修改")

def FixORFix(testrun):
    root_dir='.'
    for dirpath, dirnames, files_ in os.walk(root_dir, topdown=True):
        current_depth = dirpath[len(root_dir):].count(os.sep)
        if current_depth == 0:
            for file_ in files_:
                old_path = os.path.join(dirpath, file_)
                filename, fileext = os.path.splitext(file_)
                if fileext.lower() != ".ini":
                    continue
                new_path = os.path.join(dirpath,"DISABLED_Backup_" + filename + ".txt")
                if "DISABLED_Backup" not in filename and fileext.lower() == ".ini":
                    if not os.path.exists(new_path):
                        if not testrun:
                            try:
                                shutil.copy(old_path, new_path)
                            except Exception as e:
                                print(f"❌ 备份失败：{str(e)}")
                        else:
                            print(f"  模拟备份成功：{old_path}->{new_path}\n")
                    else:
                        print(f"存在备份项目,已跳过: {new_path}")
                with open(old_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                isAdd = 0
                for i, line in enumerate(lines):
                    if "[TextureOverride" in line:
                        isAdd = 1
                        continue
                    if "run" in line and "ORFix" in line:
                        isAdd = 0
                    if isAdd == 1 and line.startswith("["):
                        lines.insert(i,"\nrun = CommandList\\global\\ORFix\\ORFix\n")
                        isAdd = 0
                if not testrun:
                    with open(old_path, 'w', encoding='utf-8') as file:
                        file.writelines(lines)
                    print("已对根目录的ini内所有TextureOverride目标添加ORFix")
                else:
                    print("测试模拟: 修复ORFix")
            del dirnames[:]
            continue

def file_Main(limit_, testrun):
    root_dir='.'
    if not os.path.exists("./NeedMoveNode.txt"):
        print("❌ 未找到NeedMoveNode.txt文件,已生成初始文件。")
        # 生成空NeedMoveNode.txt文件
        with open("./NeedMoveNode.txt", "w", encoding='utf-8') as f:
            f.write("# 仅支持一行一个。")
            f.write("# 本文件配置注释符号: #\n")
            f.write("# ‘[’符号开头代表删除节点名为此的节点和其内容,例如: \n")
            f.write("# [CommandListExamplePosition]")
            f.write("# [CommandListExampleblend]")
            f.write("# ‘;’符号开头代表删除此注释开头的所有内容,例如: \n")
            f.write("# ;Overrides\n")
            f.write("# ;CommandList")
        input("按任意键退出")
        exit(0)
    for dirpath, dirnames, files_ in os.walk(root_dir, topdown=True):
        current_depth = dirpath[len(root_dir):].count(os.sep)
        if limit_ > 0 and limit_ < current_depth:
            del dirnames[:]
            continue
        for file_ in files_:
            file_path = os.path.join(dirpath, file_)
            filename, fileext = os.path.splitext(file_)
            if "DISABLED" not in filename and fileext.lower() == ".ini":
                line_Remove(file_path, testrun)

def line_Remove(file_path, testrun):
    NeedRemoveNode = []
    isNode = False
    NeedRemoveNote = []
    isNote = False
    with open("./NeedMoveNode.txt", "r", encoding='utf-8') as f:
            lines = f.readlines()
    for line in lines:
        if len(line) < 1 or line[0] == '#':
            continue
        else:
            if line[0] == '[':
                NeedRemoveNode.append(line[1:-1].strip())
            elif line[0] == ';':
                NeedRemoveNote.append(line[1:].strip())
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    isNode = False
    isNote = False
    for i, line in enumerate(lines):
        line_ =line.strip()
        if len(line_) == 0:
            continue
        if line_[0] == '[' and ']' in line_:
            isNode = False
            for Node in NeedRemoveNode:
                if Node in line:
                    isNode = True
                    break

        if line_[0] == ';' and "--" in line_:
        # if line_[0] == ';':
            isNote = False
            for Note in NeedRemoveNote:
                if Note in line:
                    isNote = True
                    # line_ = line_.replace(" ","")
                    # if "--" not in line_:
                    #     print("Warning,Possible non target annotations.\n")
                    #     print(line)
                    break
        if isNode or isNote:
            if line_[0] != ';':
                lines[i] = ";" + lines[i]
    if not testrun:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        print("已删除目标节点与注释区域")
    else:
        print("测试模拟: 已删除目标节点与注释区域")

def getIni(testrun,limit_):
    folder_path = select_folder()
    RemoveTexts = ["DISABLED_","Backup_","DISABLED","Backup"]
    for dirpath, dirnames, files_ in os.walk(folder_path):
        current_depth = dirpath[len(folder_path):].count(os.sep)
        if limit_ > 0 and limit_ < current_depth:
            del dirnames[:]
            continue
        for file_ in files_:
            if "DISABLED" not in file_:
                continue
            if file_.lower().endswith('.ini') or file_.lower().endswith('.txt'):
                old_path = os.path.join(dirpath, file_)
                filename, fileext = os.path.splitext(file_)
                for RemoveText in RemoveTexts:
                    filename = filename.replace(RemoveText,"")
                new_path = os.path.join(dirpath,filename + ".ini")
                if os.path.exists(new_path):
                    if not testrun:
                        try:
                            shutil.copy(old_path, new_path)
                        except Exception as e:
                            print(f"❌ 读取备份失败：{str(e)}")
                    else:
                        print(f"  模拟读取备份成功：{old_path}->{new_path}\n")
                else:
                    print("推测为非备份项目，因为其无现有项:" + old_path)

def cloneIni(testrun):
    folder_path = select_folder()
    for dirpath, dirnames, files_ in os.walk(folder_path):
        for filename in files_:
            if "DISABLED" not in filename and filename.lower().endswith('.ini'):
                old_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(dirpath, folder_path)
                new_dirpath = os.path.join(folder_path + "_back", relative_path)
                new_path = os.path.join(new_dirpath, filename)
                if not testrun:
                    try:
                        Path(new_path).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(old_path, new_path)
                    except Exception as e:
                        print(f"❌ 备份失败：{str(e)}")
                else:
                    print(f"  模拟备份成功：{old_path}->{new_path}\n")

# def select_file():
#     root = tkinter.Tk()
#     root.withdraw()
    
#     file_path = filedialog.askopenfilename(
#         title="选择文件",
#         filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")] 
#     )
#     return file_path

def select_folder():
    # 创建隐藏的根窗口
    root = tkinter.Tk()
    root.withdraw()
    
    # 打开文件夹选择对话框
    folder_path = filedialog.askdirectory(
        title="选择文件夹",
        initialdir="/"  # 可选：设置初始目录
    )
    return folder_path

# 使用示例
if __name__ == "__main__":
    print("Input Mode Num: \n1(MergePack) 2(FixORFix) ")
    print("3(RemoveNoNeedContent) 4(Clone ini files and structures)")
    mode = input("5(Roll back all ini files for this file)\n")
    testrun = False
    if mode == "1":
        packname = input("Input Packname:")
        Merage(packname ,testrun)
    elif mode == "2":
        FixORFix(testrun)
    elif mode == "3":
        print("-1 为不限制深度。")
        while True:
            try:
                limit_ = int(input("Scan depth limit: "))
                break
            except ValueError:
                print("错误：请输入一个有效的整数！")
        print("Warning, irreversible operation.")
        input("按任意键继续")
        file_Main(limit_,testrun)
    elif mode == "4":
        cloneIni(testrun) # clone ini files and structures
    elif mode == "5":
        print("-1 为不限制深度。")
        while True:
            try:
                limit_ = int(input("Scan depth limit: "))
                break
            except ValueError:
                print("错误：请输入一个有效的整数！")
        print("Warning, irreversible operation.")
        input("按任意键继续")
        getIni(testrun,limit_)
    else:
        print("No Know Input Num") 