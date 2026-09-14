#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「导航外壳 + N 套各自独立的单文件页面」融合成一个自包含单文件 HTML。

适用前提：外壳用 iframe 引用 N 个同目录的相对路径 HTML（每套图都是自包含的）。
融合后不再有任何外部文件依赖，适合上传到「一套系统只能是一个文件」的托管平台。

原理
----
把 N 套图的完整 HTML 源码，以 `<script type="text/plain" id="src-<id>">` 的
**明文块**内嵌进外壳，切换时取出来交给 iframe 的 `srcdoc` 渲染。

为什么这么做（而不是把 N 套图直接拼进同一个 document）：
  - 每套图都自带 `<style>` 与顶层 `const` / `function`，直接拼会立刻撞选择器与重复声明；
  - `srcdoc` 生成的是**独立 document**，CSS/JS 作用域天然隔离 → **一套图都不用改**，
    已经验证过的页面保持逐字不变，风险最低；
  - 比 Shadow DOM 改造省事得多，也不必给每个选择器加前缀。

为什么不 base64：明文块可以直接 grep，后续改动仍能定位；base64 会 +33% 体积且不可读。

用法
----
    python3 merge_single_file.py --shell path/to/shell.html \
                                 --out   path/to/merged.html \
                                 --pairs '{"gemini":"gemini-35-flash.html", "ds":"deepseek.html"}'
    # --pairs 的 key 必须与外壳 MODELS 里的 id 一致；value 是相对 --dir 的文件名
    # --dir 默认为 shell 所在目录

外壳需要满足的三点（脚本会断言）：
  1. MODELS 数组每项形如 `{ id:'x', ...,\n    file:'x.html', color:... }` —— file 字段会被删掉；
  2. 有 `/* ---------------- 切换模型 ---------------- */\nlet current = '';` 锚点；
  3. 有 `    pane.src = m.file;` 一行。
"""
import argparse, io, json, os, re, sys


def esc(t):
    """内嵌进 script[type=text/plain] 只需防住 </script 与 <!-- 两个序列。"""
    if '<\\/script' in t:
        raise SystemExit('原文里已存在转义串 <\\/script，会与本次转义冲突')
    return t.replace('</script', '<\\/script').replace('<!--', '<\\!--')


def unesc(t):
    return t.replace('<\\/script', '</script').replace('<\\!--', '<!--')


HELPER = r'''/* ---------------- 内嵌页源码（单文件融合） ----------------
   N 套图以 script[type=text/plain]、id 形如 src-<模型id> 的明文块内嵌在本文件里，
   切换时取出、还原转义，交给 iframe 的 srcdoc 渲染。
   srcdoc 生成的是独立 document，所以各套图的 CSS/JS 互不干扰。 */
const PAGE_SRC = {};
document.querySelectorAll('script[type="text/plain"][id^="src-"]').forEach(el => {
  PAGE_SRC[el.id.slice(4)] = el.textContent
    .split('<\\/script').join('</script')
    .split('<\\!--').join('<!--');
});
function srcOf(id){
  return PAGE_SRC[id] ||
    '<!DOCTYPE html><html><body style="margin:0;height:100%;background:#000;color:#8A93A3;' +
    'font:13px -apple-system,BlinkMacSystemFont,\'PingFang SC\',sans-serif;display:flex;' +
    'align-items:center;justify-content:center">该页缺失</body></html>';
}

/* ---------------- 切换模型 ---------------- */
let current = '';'''

OLD_SWITCH = "/* ---------------- 切换模型 ---------------- */\nlet current = '';"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shell', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--dir', default=None, help='N 套图所在目录，默认 = shell 所在目录')
    ap.add_argument('--pairs', required=True, help='JSON: {"<id>":"<file>", ...}')
    a = ap.parse_args()
    d = a.dir or os.path.dirname(os.path.abspath(a.shell))
    pairs = json.loads(a.pairs)
    if not pairs:
        raise SystemExit('--pairs 为空')

    shell = io.open(a.shell, encoding='utf-8').read()

    # 1. 读数、转义、组装内嵌块
    blocks, raw = [], {}
    for mid, fn in pairs.items():
        p = os.path.join(d, fn)
        t = io.open(p, encoding='utf-8').read()
        raw[mid] = t
        blocks.append('<script type="text/plain" id="src-%s">%s</script>' % (mid, esc(t)))
        print('  内嵌 %-10s %-44s %8d 字符' % (mid, fn, len(t)))
    payload = '\n'.join(blocks)
    print('内嵌总字符 = %d' % len(payload))

    # 2. 插到主 <script> 之前
    anchor = '\n<script>\n/* 侧栏条目。'
    if shell.count(anchor) != 1:
        raise SystemExit('主 <script> 锚点不唯一（%d）' % shell.count(anchor))
    shell = shell.replace(
        anchor,
        '\n\n<!-- ===== 以下是内嵌的完整页面（script type=text/plain，不会被执行） ===== -->\n'
        + payload +
        '\n<!-- ===== 内嵌结束 ===== -->\n\n<script>\n/* 侧栏条目。', 1)

    # 3. MODELS 去掉 file 字段
    before = len(re.findall(r"file:'", shell))
    shell = re.sub(r"\n\s*file:'[^']*',", '', shell)
    after = len(re.findall(r"file:'", shell))
    if before != len(pairs) or after != 0:
        raise SystemExit('MODELS 的 file 字段处理异常 %d -> %d（期望 %d -> 0）'
                         % (before, after, len(pairs)))
    print('MODELS 去掉 file 字段：%d -> %d' % (before, after))

    # 4. 注入 PAGE_SRC / srcOf
    if shell.count(OLD_SWITCH) != 1:
        raise SystemExit('切换模型锚点不唯一')
    shell = shell.replace(OLD_SWITCH, HELPER, 1)

    # 5. show() 改用 srcdoc
    if shell.count('    pane.src = m.file;') != 1:
        raise SystemExit('pane.src 锚点不唯一')
    shell = shell.replace('    pane.src = m.file;', '    pane.srcdoc = srcOf(id);', 1)

    # 5b. 兜底提示往往还引用 m.file（已删）→ 会把 undefined 渲染进页面，必须一起处理。
    #     顺手把紧邻上方那行「const m = MODELS.find(...)」也删掉：它只为这条提示存在，
    #     留着会变成未使用变量（无害但不干净）。按「行」处理最稳，不去猜嵌套引号。
    if 'm.file' in shell:
        fixed = []
        for line in shell.split('\n'):
            if 'm.file' in line:
                indent = line[:len(line) - len(line.lstrip())]
                if fixed and re.search(r"const\s+m\s*=\s*MODELS\.find", fixed[-1]):
                    fixed.pop()
                fixed.append(indent + "bootTx.textContent = "
                             "'渲染较慢，请稍候或刷新页面（本页为单文件，无需其它依赖）';")
            else:
                fixed.append(line)
        shell = '\n'.join(fixed)
        if 'm.file' in shell:
            raise SystemExit('仍有 m.file 残留，请手工处理')
        print('兜底提示已改为不依赖外部文件')

    io.open(a.out, 'w', encoding='utf-8').write(shell)
    print('已写出 %s（%d 字符 / %.2f MB）'
          % (a.out, len(shell), len(shell.encode('utf-8')) / 1048576))

    # 6. 往返校验：抽出内嵌块 → 还原 → 与原文逐字比对
    fails = []
    for mid in pairs:
        m = re.search(r'<script[^>]*id="src-%s"[^>]*>(.*?)</script>' % mid, shell, re.S)
        if not m:
            fails.append('找不到内嵌块 ' + mid); continue
        if unesc(m.group(1)) != raw[mid]:
            fails.append('往返不一致 ' + mid)
    if fails:
        raise SystemExit('往返校验失败：' + str(fails))
    print('往返校验：全部 %d 套逐字一致' % len(pairs))

    # 7. 结构自检（别用 rfind('<script>')，内嵌正文里也有 <script>）
    print('自检：真实 </script> = %d（应为 %d 内嵌 + 1 主 + 平台注入的 1）'
          % (shell.count('</script>'), len(pairs)))
    print('自检：转义串 = %d（应为 %d）' % (shell.count('<\\/script'), len(pairs)))


if __name__ == '__main__':
    main()
