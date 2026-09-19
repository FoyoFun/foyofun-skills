# -*- coding: utf-8 -*-
"""摘录器：只把角色名命中处的上下文窗口（或高密度整章）抽出来，合成一个文件。
这是整个流程里最核心的省 token 步骤——用少量原文覆盖大部分角色相关内容。

用法:
python excerpt.py <文本目录> <输出文件> --names 名1,名2 [--before 20] [--after 20] \
    [--chapter-full 8] [--per-file-cap 80000] [--total-cap 120000] \
    [--files f1,f2,...] [--append]

参数:
  --names          所有名字变体，逗号分隔
  --before/--after 命中行前后的窗口行数（默认 20/20）
  --chapter-full   单章（按 # 开头的标题行分章）命中数达到该值则整章收录（默认 8）；
                   设为 999 即纯窗口模式（无整章收录）
  --per-file-cap   单个源文件的摘录字符上限（默认 80000）
  --total-cap      全部摘录的总字符上限（默认 120000）。超出时按各文件原始体量比例
                   分摊预算；段级超限采取"截断保留头部"而非整段丢弃
  --files          只处理指定文件（逗号分隔的文件名片段）。指定时不做 total-cap
                   比例分摊（每文件用满 per-file-cap），用于给主场卷做全量补跑
  --append         追加到输出文件末尾而非覆盖，用于增量补跑合并
  --skip           跳过章节标题含这些关键词的命中（默认 后记,附录,简介,版权,插图,目录）

输出会打印 摘录字数/原文总字数/覆盖率%。段被截断/丢弃时会内联标注。
已知盲区（接受）: 角色仅以"她/姐姐"等代词出场、名字未出现的段落会漏；
--chapter-full 的整章收录是对主场章节的补偿。
"""
import sys, os, re, glob, argparse
from collections import defaultdict

def build_segs(lines, names, before, after, chapter_full, skip_words):
    chap_of = []
    chap_title = '(无标题)'
    for i, l in enumerate(lines):
        if l.startswith('#'):
            chap_title = l.lstrip('# ').strip() or chap_title
        chap_of.append(chap_title)
    hit_lines = [i for i, l in enumerate(lines) if any(n in l for n in names)
                 and not any(w in chap_of[i] for w in skip_words)]
    if not hit_lines:
        return None
    chap_hits = defaultdict(list)
    for i in hit_lines:
        chap_hits[chap_of[i]].append(i)
    segs, done = [], set()
    for title, hs in chap_hits.items():
        if len(hs) >= chapter_full:
            rng = [i for i in range(len(lines)) if chap_of[i] == title]
            segs.append((rng[0], rng[-1] + 1, len(hs)))
            done.add(title)
    merged = []
    for i in sorted(i for i in hit_lines if chap_of[i] not in done):
        s, e = max(0, i - before), min(len(lines), i + after + 1)
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e); merged[-1][2] += 1
        else:
            merged.append([s, e, 1])
    segs += [tuple(m) for m in merged]
    segs.sort()
    return chap_of, segs

def render(fname, lines, chap_of, segs, budget):
    """按命中密度从高到低装填；单段超预算则截断保留头部，零头不足2000字才整段丢弃。"""
    kept, dropped, used = [], 0, 0
    for seg in sorted(segs, key=lambda s: -s[2]):
        s, e, h = seg
        c = sum(len(lines[i]) + 1 for i in range(s, e))
        if used + c <= budget:
            kept.append((s, e, h, '')); used += c
        else:
            remain = budget - used
            if remain > 2000:
                cut, acc = e, 0
                for i in range(s, e):
                    acc += len(lines[i]) + 1
                    if acc > remain:
                        cut = i; break
                kept.append((s, cut, h, '  [本段超预算，已截断]')); used = budget
            else:
                dropped += 1
    kept.sort()
    parts = []
    if dropped:
        parts.append(f'[注] 预算耗尽，另丢弃 {dropped} 个低密度窗口（--files 补跑可找回）')
    for s, e, h, note in kept:
        parts.append(f'\n--- {fname} · {chap_of[s]} (命中{h}){note} ---')
        parts.append('\n'.join(lines[s:e]).strip())
    text = '\n'.join(parts)
    return text, len(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--names', required=True)
    ap.add_argument('--before', type=int, default=20)
    ap.add_argument('--after', type=int, default=20)
    ap.add_argument('--chapter-full', type=int, default=8)
    ap.add_argument('--per-file-cap', type=int, default=80000)
    ap.add_argument('--total-cap', type=int, default=120000)
    ap.add_argument('--files', default='')
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--skip', default='后记,附录,简介,版权,插图,目录')
    a = ap.parse_args()
    names = [x for x in a.names.split(',') if x]
    wanted = [x for x in a.files.split(',') if x]
    skip_words = [x for x in a.skip.split(',') if x]
    files = sorted(glob.glob(os.path.join(a.src, '*.txt')))
    if wanted:
        files = [f for f in files if any(w in os.path.basename(f) for w in wanted)]
    if not files:
        print('没有匹配的源文件'); sys.exit(1)

    parsed = []
    total_src = 0
    for f in files:
        lines = open(f, encoding='utf-8').read().splitlines()
        total_src += sum(len(l) + 1 for l in lines)
        r = build_segs(lines, names, a.before, a.after, a.chapter_full, skip_words)
        if r:
            parsed.append((os.path.basename(f), lines, r[0], r[1]))
    if not parsed:
        print('所有文件中都没有命中'); sys.exit(1)

    # 预算分配: 全量跑且超总上限时按体量比例分摊; --files 补跑时不分摊
    natural = {fn: sum(len(lines[i]) + 1 for s, e, h in segs for i in range(s, e))
               for fn, lines, _, segs in parsed}
    total_nat = sum(natural.values())
    scale = (not wanted) and total_nat > a.total_cap
    budget = {fn: (a.per_file_cap if not scale
                   else max(2000, min(a.per_file_cap, round(a.total_cap * v / total_nat))))
              for fn, v in natural.items()}

    blocks = []
    for fn, lines, chap_of, segs in parsed:
        txt, _ = render(fn, lines, chap_of, segs, budget[fn])
        blocks.append((fn, txt))
    if a.append and os.path.exists(a.out):
        # 同名文件的旧块被新块替换（避免补跑后重复读入），其余文件原序保留
        prev = open(a.out, encoding='utf-8').read()
        old = {}
        for m in re.finditer(r'\n\n===== (.+?) =====\n(.*?)(?=\n\n===== |$)', prev, re.S):
            old[m.group(1)] = m.group(2)
        new_names = {fn for fn, _ in blocks}
        merged = [(fn, txt) for fn, txt in old.items() if fn not in new_names]
        merged += blocks
        text = ''.join(f'\n\n===== {fn} =====\n{txt}' for fn, txt in merged)
    else:
        text = ''.join(f'\n\n===== {fn} =====\n{txt}' for fn, txt in blocks)
    open(a.out, 'w', encoding='utf-8').write(text)
    print(f'摘录 {len(text)} 字 / 原文 {total_src} 字 = {len(text) * 100 // max(total_src, 1)}%  -> {a.out}')
    if scale:
        print(f'[注] 原始摘录 {total_nat} 字超过总上限 {a.total_cap}，已按文件体量比例分摊预算（段级截断保留）')
        print('[提示] 主场卷被截断时，用 --files 卷号 --per-file-cap 80000 --append 单独补跑该卷')

if __name__ == '__main__':
    main()
