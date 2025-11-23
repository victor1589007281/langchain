#!/usr/bin/env python3
"""验证 Markdown 文件中的 Mermaid 图表语法"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def extract_mermaid_blocks(content: str) -> List[Tuple[int, str]]:
    """提取所有 Mermaid 代码块及其行号"""
    blocks = []
    lines = content.split('\n')
    in_mermaid = False
    block_start = 0
    current_block = []
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```mermaid'):
            in_mermaid = True
            block_start = i
            current_block = []
        elif line.strip() == '```' and in_mermaid:
            in_mermaid = False
            blocks.append((block_start, '\n'.join(current_block)))
        elif in_mermaid:
            current_block.append(line)
    
    return blocks

def validate_mermaid_syntax(mermaid_code: str) -> List[str]:
    """基本的 Mermaid 语法验证"""
    errors = []
    lines = mermaid_code.strip().split('\n')
    
    if not lines:
        errors.append("空的 Mermaid 代码块")
        return errors
    
    # 检查图表类型
    graph_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                   'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'gantt', 
                   'pie', 'mindmap']
    
    first_line = lines[0].strip()
    has_valid_type = any(first_line.startswith(gt) for gt in graph_types)
    
    if not has_valid_type:
        errors.append(f"无效的图表类型: {first_line}")
        return errors
    
    # 判断图表类型
    is_class_diagram = first_line.startswith('classDiagram')
    
    # 检查常见语法错误（classDiagram 不检查花括号）
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('%'):
            continue
            
        # 检查未闭合的引号
        if line_stripped.count('"') % 2 != 0:
            errors.append(f"第 {i} 行: 未闭合的引号")
        
        # 只在非 classDiagram 中检查括号（classDiagram 不使用花括号定义类）
        if not is_class_diagram:
            # 检查括号匹配
            if line_stripped.count('[') != line_stripped.count(']'):
                errors.append(f"第 {i} 行: 方括号不匹配")
            if line_stripped.count('(') != line_stripped.count(')'):
                errors.append(f"第 {i} 行: 圆括号不匹配")
            if line_stripped.count('{') != line_stripped.count('}'):
                errors.append(f"第 {i} 行: 花括号不匹配")
    
    return errors

def validate_file(file_path: Path) -> bool:
    """验证单个文件"""
    print(f"\n{'='*60}")
    print(f"验证文件: {file_path.name}")
    print(f"{'='*60}")
    
    content = file_path.read_text(encoding='utf-8')
    blocks = extract_mermaid_blocks(content)
    
    print(f"找到 {len(blocks)} 个 Mermaid 图表")
    
    all_valid = True
    for i, (line_num, block) in enumerate(blocks, 1):
        errors = validate_mermaid_syntax(block)
        if errors:
            all_valid = False
            print(f"\n❌ 图表 #{i} (第 {line_num} 行) 存在问题:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"✅ 图表 #{i} (第 {line_num} 行) 语法正确")
    
    return all_valid

def main():
    vdocs_dir = Path(__file__).parent
    md_files = sorted(vdocs_dir.glob('*.md'))
    
    if not md_files:
        print("未找到 Markdown 文件")
        return 1
    
    print(f"开始验证 {len(md_files)} 个文档...")
    
    all_valid = True
    total_charts = 0
    
    for md_file in md_files:
        if not validate_file(md_file):
            all_valid = False
        # 统计图表数量
        content = md_file.read_text(encoding='utf-8')
        blocks = extract_mermaid_blocks(content)
        total_charts += len(blocks)
    
    print(f"\n{'='*60}")
    print(f"共检查 {len(md_files)} 个文档，{total_charts} 个 Mermaid 图表")
    if all_valid:
        print("✅ 所有 Mermaid 图表语法验证通过!")
    else:
        print("❌ 发现语法错误，请修复后重新验证")
    print(f"{'='*60}\n")
    
    return 0 if all_valid else 1

if __name__ == '__main__':
    sys.exit(main())
