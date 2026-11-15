#!/usr/bin/env python3
"""スキルの点検と、アップロード用 zip の作成。

使い方:  python3 scripts/build_skills.py
結果:    dist/<スキル名>.zip  （claude.ai の「スキル」にアップロードするファイル）
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"


def frontmatter(text):
    """SKILL.md 冒頭の --- で囲まれた部分から name と description を取り出す。"""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, None
    block = m.group(1)
    name = re.search(r"^name:\s*(.+)$", block, re.M)
    name = name.group(1).strip().strip('"') if name else None
    d = re.search(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)", block, re.M | re.S)
    desc = d.group(1).strip() if d else None
    if desc and desc[0] in "|>":                       # 複数行の書き方
        desc = "\n".join(line.strip() for line in desc[1:].strip().splitlines())
    elif desc:
        desc = desc.strip('"').replace("\\n", "\n")
    return name, desc


def check(skill_dir, all_names):
    errors, warnings = [], []
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return ["SKILL.md がない"], warnings
    text = md.read_text(encoding="utf-8")
    name, desc = frontmatter(text)
    if name != skill_dir.name:
        errors.append(f"name（{name}）がフォルダ名と違う")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", skill_dir.name):
        errors.append("スキル名は、半角の小文字・数字・ハイフンで64字以内")
    if not desc:
        errors.append("description がない")
    elif len(desc) > 1024:
        errors.append(f"description が長い（{len(desc)}字。1,024字以内）")
    lines = text.count("\n") + 1
    if lines > 500:
        warnings.append(f"SKILL.md が{lines}行（500行以内が目安。詳細は references/ へ）")
    all_text = "\n".join(p.read_text(encoding="utf-8") for p in skill_dir.rglob("*.md"))
    for ref in sorted(set(re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`", all_text))):
        if (skill_dir / ref).exists():
            continue
        if any((d / ref).exists() for d in SKILLS.iterdir() if d.is_dir()):
            continue                                   # 他のスキルの参照ファイルを指している
        errors.append(f"参照先のファイルがない: {ref}")
    for other in sorted(set(re.findall(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`", text))):
        if other not in all_names and other not in KNOWN_EXTERNAL:
            warnings.append(f"スキル名らしい語 `{other}` が、このリポジトリにない")
    return errors, warnings


# このリポジトリの外にあるスキルや、スキル名ではない語
KNOWN_EXTERNAL = {"pptx", "docx", "xlsx", "pdf", "dataviz", "deep-research", "skill-creator",
                  "japanize-matplotlib", "matplotlib-fontja", "numpy-financial", "e-stat",
                  "scikit-learn", "t-sne", "k-means", "getis-ord", "frontend-design",
                  "file-reading", "pdf-reading", "prefers-reduced-motion"}


def build(skill_dir):
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(skill_dir.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store":
                z.write(p, p.relative_to(SKILLS).as_posix())
    return out


def main():
    dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    names = {d.name for d in dirs}
    failed = False
    for d in dirs:
        errors, warnings = check(d, names)
        mark = "NG" if errors else "OK"
        print(f"[{mark}] {d.name}")
        for e in errors:
            print(f"      エラー: {e}")
        for w in warnings:
            print(f"      注意  : {w}")
        if errors:
            failed = True
        else:
            build(d)
    print(f"\n{len(dirs)}本を点検。zip は {DIST.relative_to(ROOT)}/ に出力。")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
