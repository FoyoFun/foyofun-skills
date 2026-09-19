# -*- coding: utf-8 -*-
"""引文校验: 检查档案 md 里 blockquote(> 开头) 引文是否逐字存在于原文。
片段级匹配: 引文按 ……/各种引号切成分片，任一 >=12 字分片命中即通过——
这样"用……拼接多段"、"叙述包进引号"的引法不会误报。

用法: python verify_quotes.py <档案.md> <文本目录>

判读零命中清单:
  - 以 说明/依据/译名/（ 开头 → 多为编辑性注释，不是引文，忽略
  - 其余 → 到原文 grep 核实: 确属漏字/改写就修正档案；原文本来如此则加（原文如此）
"""
import sys, re, glob, os

TR = str.maketrans({',': '，', '.': '。', '!': '！', '?': '？',
                    '"': '「', "'": '‘', '“': '「', '”': '」', '’': '’'})

def N(s):
    return re.sub(r'\s+', '', s).translate(TR)

def fragments(q):
    q = re.sub(r'（[^）]*(卷|语|原文如此|系原文|为原文|错字|照录|场面|中略|第\d|备注)[^）]*）', '', q).strip()
    q = re.sub(r'^[「『“"]+', '', q)
    q = re.sub(r'[」』”"]+$', '', q)
    parts = re.split(r'……|「|」|『|』|‘|’', q)
    return [N(p) for p in parts if len(N(p)) >= 12]

def main():
    profile, src = sys.argv[1], sys.argv[2]
    srcs = [N(open(f, encoding='utf-8').read()) for f in glob.glob(os.path.join(src, '*.txt'))]
    if not srcs:
        print('源目录没有 txt'); sys.exit(1)
    big = '\n'.join(srcs)
    t = open(profile, encoding='utf-8').read()
    qs = [re.sub(r'^>\s*', '', l.strip()) for l in t.splitlines() if l.strip().startswith('>')]
    zero = []
    for q in qs:
        frs = fragments(q)
        if frs and not any(fr in big for fr in frs):
            zero.append(q)
    print(f'引文总数 {len(qs)}，零命中 {len(zero)}')
    for z in zero:
        tag = '注释?' if re.match(r'^(说明|依据|译名|（|关于)', z) else '需核对'
        print(f'  [{tag}] {z[:100]}')

if __name__ == '__main__':
    main()
