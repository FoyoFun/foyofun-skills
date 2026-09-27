# -*- coding: utf-8 -*-
"""名字密度侦察：统计每个文本文件中角色名（含变体）的出现次数，辅助分层与变体验证。

用法: python scan.py <文本目录> 名字1 [名字2 ...]
输出: 按文件列出各变体计数与合计，最后给总量。
用法要点:
  - 把所有已知变体都传进来（如 佑巳 祐巳），计数为 0 的变体可弃用
  - 若姓氏出现次数远多于名字合计，说明还有未发现的变体（常见：形近字/简繁/异体）
  - 单字名（如"令"）会有大量误命中（命令/令和…），密度仅供参考，摘录时靠上下文过滤
"""
import sys, glob, os
from pathlib import Path

def main():
    src, names = sys.argv[1], sys.argv[2:]
    if not names:
        print('用法: python scan.py <文本目录> 名字1 [名字2 ...]'); sys.exit(1)
    files = sorted(glob.glob(os.path.join(src, '*.txt')))
    if not files:
        print('目录下没有 txt:', src); sys.exit(1)
    totals = [0] * len(names)
    print('file\t' + '\t'.join(names) + '\tTOTAL')
    for f in files:
        t = open(f, encoding='utf-8').read()
        cs = [t.count(n) for n in names]
        totals = [a + b for a, b in zip(totals, cs)]
        print(f'{os.path.basename(f)}\t' + '\t'.join(map(str, cs)) + f'\t{sum(cs)}')
    print('TOTAL\t' + '\t'.join(map(str, totals)) + f'\t{sum(totals)}')
    for n in names:
        if len(n) == 1:
            print(f'[警告] "{n}" 是单字名，计数含大量误命中，仅供粗略参考')

if __name__ == '__main__':
    main()
