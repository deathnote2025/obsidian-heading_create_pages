# script.py
import sys
import os
import re
import os
def extract_alias(title):
    # 匹配中文括号或英文括号中的内容
    alias_pattern = re.compile(r'[（(]([^）)]+)[）)]')
    match = alias_pattern.search(title)
    return match.group(1) if match else None

def clean_title(title):
    # 移除数字和点（如1., 1.1., 等）
    cleaned = re.sub(r'^\d+(\.\d+)*\.?\s*', '', title)
    # 提取括号前的内容作为标题
    cleaned = re.sub(r'\s*[（(][^）)]+[）)]', '', cleaned)
    return cleaned.strip()

def remove_bold_marks(text):
    # 移除文本中的**标记
    return re.sub(r'\*\*([^*]+)\*\*', r'\1', text)

def process_content(content, output_file, output_dir='.', max_header_level=2, keep_header_marks=False):
    lines = content.split('\n')
    header_pattern = re.compile(r'^(#{1,' + str(max_header_level) + '})\s+(.+)$', re.MULTILINE)
    has_headers = False
    for line in lines:
        if header_pattern.match(line):
            has_headers = True
            print(f"Found header: {line}")
            break
    if not has_headers:
        print("No headers found in the content")
        return
    
    print(f"Processing content with max_header_level: {max_header_level}")
    main1_content = []
    current_files = {i: {'file': None, 'content': [], 'alias': None} for i in range(1, max_header_level + 1)}
    
    # 收集标题前的内容
    pre_header_content = []
    for line in lines:
        if header_pattern.match(line):
            break
        if line.strip():  # 只添加非空行
            pre_header_content.append(line)
    
    for line in lines:
        match = header_pattern.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2)
            alias = extract_alias(title)
            clean_title_text = clean_title(title)
            print(f"Processing header: {clean_title_text} (level {level})")
            
            # 将标题添加到main1.md
            if keep_header_marks:
                main1_content.append('#' * level + f' [[{clean_title_text}]]')
            else:
                main1_content.append(f'[[{clean_title_text}]]')
            
            # 保存当前级别之前的所有内容
            for l in range(level, max_header_level + 1):
                if current_files[l]['file'] and current_files[l]['content']:
                    file_content = []
                    if current_files[l]['alias']:
                        file_content.extend([
                            '---',
                            'aliases:',
                            f'  - {current_files[l]["alias"]}',
                            '---',
                            ''
                        ])
                    if l == 1 and pre_header_content:
                        file_content.extend(pre_header_content)
                        file_content.append('')
                    file_content.extend(current_files[l]['content'])
                    
                    # 确保文件路径存在
                    file_path = os.path.join(output_dir, current_files[l]['file'] + '.md')
                    print(f"Creating file: {file_path}")
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(file_content))
                
                if l >= level:
                    current_files[l]['file'] = None
                    current_files[l]['content'] = []
                    current_files[l]['alias'] = None
            
            current_files[level]['file'] = clean_title_text
            current_files[level]['content'] = []
            current_files[level]['alias'] = alias
        else:
            cleaned_line = remove_bold_marks(line)
            for level in range(max_header_level, 0, -1):
                if current_files[level]['file']:
                    current_files[level]['content'].append(cleaned_line)
                    break
    
    # 保存最后的文件内容
    for level in range(1, max_header_level + 1):
        if current_files[level]['file'] and current_files[level]['content']:
            file_content = []
            if current_files[level]['alias']:
                file_content.extend([
                    '---',
                    'aliases:',
                    f'  - {current_files[level]["alias"]}',
                    '---',
                    ''
                ])
            file_content.extend(current_files[level]['content'])
            
            # 确保文件路径存在
            file_path = os.path.join(output_dir, current_files[level]['file'] + '.md')
            print(f"Creating file: {file_path}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(file_content))
    
    # 保存main1.md
    output_content = []
    if pre_header_content:
        output_content.extend(pre_header_content)
        output_content.append('')
    output_content.extend(main1_content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_content))

def get_max_header_level(content):
    # 匹配所有标题行
    header_pattern = re.compile(r'^(#{1,6})\s+.+$', re.MULTILINE)
    headers = header_pattern.findall(content)
    if not headers:
        return 2  # 如果没有找到标题，默认返回2
    # 返回最小的标题级别（#号最少的标题）
    return min(len(h) for h in headers)

def process_one_level(input_file, output_file=None, create_folder=True, header_level=None, keep_header_marks=False):
    # 如果output_file未指定，使用input_file作为默认值
    if output_file is None:
        output_file = input_file
    
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查文档是否包含标题
    header_pattern = re.compile(r'^#{1,6}\s+.+$', re.MULTILINE)
    if not header_pattern.search(content):
        print(f"No headers found in {input_file}")
        return
    
    # 如果需要创建文件夹
    output_dir = os.path.join(os.path.dirname(input_file), os.path.splitext(os.path.basename(input_file))[0]) if create_folder else '.'
    if create_folder and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 如果没有指定header_level，自动检测最高级别的标题
    if header_level is None:
        header_level = get_max_header_level(content)
        print(f"Detected header level: {header_level}")
    
    process_content(content, output_file, output_dir, header_level, keep_header_marks)

def process_all_md_files(directory):
    # 遍历目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 只处理.md文件
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                print(f'Processing: {file_path}')
                process_one_level(file_path, create_folder=True, keep_header_marks=False)

def process_n_level(file_name,num_of_levels):
    '''
    file_name = "心理学"
    生成一个文件夹的 n级标题
    '''
    process_one_level(f'{file_name}.md', create_folder=True, keep_header_marks=False)
    n = 1
    while n <num_of_levels:
        process_all_md_files(file_name)
        n+=1


# process_n_level(file_name='main 1',num_of_levels=2)


def main():
    # 从命令行获取传入的参数
    args = sys.argv[1:]
    print(f"Received arguments: {args}")
    print("Hello from Python!")
    # base_path是笔记的主路径
    script_path = sys.argv[0]  # 获取脚本的完整路径
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_path)))) 
    print(base_path)
    file_name = os.path.join(base_path,args[0].split('.')[0])
    process_n_level(file_name=file_name,num_of_levels=int(args[1]))
if __name__ == "__main__":
    main()
