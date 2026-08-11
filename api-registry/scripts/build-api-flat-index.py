#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 注册表扁平索引生成工具

从 api-registry/ 下的分类 .md 文件中提取所有 API 条目（### 标题行），
生成 _flat_index.md，供 AI 一次 Read 即可扫描全部 API，避免逐文件遍历。

提取规则：
  - 从 ## 标题提取模块名（如 TimeUtil）
  - 从 ### 标题提取 API 签名（如 `GetServerTimeInSec() → number`）
  - 从紧跟的文本行提取一句话说明
  - 从分类 _index.md 获取分类名和文件名映射

用法:
    python build-api-flat-index.py --root <API_REGISTRY_DIR>

输出:
    在 <API_REGISTRY_DIR>/_flat_index.md 生成扁平索引
"""
import os
import re
import sys
import argparse
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

HEADER = """# API 注册表扁平索引

> 自动生成于：{timestamp}
> 每行一个 API，供 AI 快速扫描和语义匹配。请勿手动编辑此文件。

| 分类 | 模块 | API 签名 | 说明 | 路径 |
|------|------|---------|------|------|
"""

FOOTER = """
> 💡 **使用方法**：AI 先读此文件（一次 Read）定位目标 API，再 Read 对应分类文件查看详情。
"""

def parse_timestamp():
    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %z')

def extract_from_md(filepath):
    """从分类 .md 文件中提取所有 API 条目。

    返回: [(module_name, api_signature, description, anchor), ...]
    """
    entries = []
    if not filepath.exists():
        return entries

    content = filepath.read_text(encoding='utf-8', errors='replace')
    lines = content.split('\n')

    current_module = None

    for i, line in enumerate(lines):
        line = line.rstrip()

        # ## 标题 → 模块名
        m_module = re.match(r'^##\s+(.+?)$', line)
        if m_module:
            current_module = m_module.group(1).strip()
            continue

        # ### 标题 → API 签名
        m_api = re.match(r'^###\s+(.+?)$', line)
        if not m_api or current_module is None:
            continue

        api_sig = m_api.group(1).strip()
        # Remove backticks from signature
        api_sig_clean = api_sig.strip('`')

        # 提取说明（紧跟 ### 下方的第一行非空文本）
        desc = ""
        for j in range(i + 1, min(i + 10, len(lines))):
            next_line = lines[j].rstrip()
            if not next_line:
                continue
            if re.match(r'^#{1,4}\s', next_line):
                break
            if next_line.startswith('---'):
                break
            # Skip bold markers and backtick-only lines
            if next_line.startswith('**') and next_line.endswith('**'):
                continue
            desc = next_line.strip()
            break

        # Generate anchor
        anchor = api_sig_clean.lower()
        anchor = re.sub(r'[^a-z0-9→\s]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)

        entries.append((current_module, api_sig_clean, desc, anchor))

    return entries

def load_category_map(root_dir):
    """从 _index.md 读取分类名→文件名的映射。"""
    cat_map = {}
    index_file = root_dir / '_index.md'
    if not index_file.exists():
        return cat_map

    content = index_file.read_text(encoding='utf-8', errors='replace')
    # 匹配表格行: | 分类名 | `filename.md` | 描述 |
    for line in content.split('\n'):
        m = re.match(r'\|\s*(.+?)\s*\|\s*`(.+?\.md)`\s*\|', line)
        if m:
            cat_name = m.group(1).strip()
            filename = m.group(2).strip()
            cat_map[filename] = cat_name

    return cat_map

def build_flat_index(root_dir):
    """主函数：遍历分类文件，提取 API，生成 _flat_index.md。"""
    root = Path(root_dir)
    if not root.exists():
        print(f"Error: {root_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    cat_map = load_category_map(root)

    # 收集所有 .md 文件（排除索引文件）
    md_files = sorted([
        f for f in root.glob('*.md')
        if not f.name.startswith('_')
    ])

    all_entries = []
    for md_file in md_files:
        entries = extract_from_md(md_file)
        cat_name = cat_map.get(md_file.name, md_file.stem)

        for module, sig, desc, anchor in entries:
            all_entries.append({
                'category': cat_name,
                'module': module,
                'signature': sig,
                'description': desc,
                'path': f"{md_file.name}#{anchor}"
            })

    # 生成输出
    lines = [HEADER.strip().format(timestamp=parse_timestamp())]

    for entry in all_entries:
        desc = entry['description'][:80]  # 截断过长的描述
        line = f"| {entry['category']} | {entry['module']} | `{entry['signature']}` | {desc} | {entry['path']} |"
        lines.append(line)

    lines.append(FOOTER.strip())

    output = '\n'.join(lines) + '\n'

    # 写文件
    out_path = root / '_flat_index.md'
    out_path.write_text(output, encoding='utf-8')

    print(f"✅ Generated {out_path}")
    print(f"   {len(all_entries)} APIs from {len(md_files)} category files")

    return len(all_entries), len(md_files)

def main():
    parser = argparse.ArgumentParser(description='Build API registry flat index')
    parser.add_argument('--root', required=True, help='API registry root directory')
    parser.add_argument('--dry-run', action='store_true', help='Only print stats')
    args = parser.parse_args()

    if args.dry_run:
        root = Path(args.root)
        md_files = sorted([f for f in root.glob('*.md') if not f.name.startswith('_')])
        total = sum(len(extract_from_md(f)) for f in md_files)
        print(f"[DRY RUN] {total} APIs from {len(md_files)} files")
        return

    build_flat_index(args.root)

if __name__ == '__main__':
    main()
