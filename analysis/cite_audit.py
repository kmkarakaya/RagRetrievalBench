"""Citation audit (A24): cited keys vs refs.bib entries; missing/unused/incomplete."""
import re
import glob

CITE = re.compile(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")

cited = set()
for f in glob.glob("journal_paper/*.tex"):
    s = open(f, encoding="utf-8").read()
    for m in CITE.finditer(s):
        for k in m.group(1).split(","):
            k = k.strip()
            if k:
                cited.add(k)

btxt = open("journal_paper/refs.bib", encoding="utf-8").read()
entries = {}
for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)(?=\n@|\Z)", btxt, re.S):
    entries[m.group(2).strip()] = (m.group(1).lower(), m.group(3))
bibkeys = set(entries)


def has_field(block, name):
    return re.search(r"(?im)^\s*" + name + r"\s*=", block) is not None


print("cited keys:", len(cited), "| bib entries:", len(bibkeys))
print("\nMISSING (cited, not in refs.bib):", sorted(cited - bibkeys) or "NONE")
unused = sorted(bibkeys - cited)
print(f"\nUNUSED (in refs.bib, never cited): {len(unused)}")
for k in unused:
    print("   -", k)
print("\nCITED entries missing author/title/year:")
bad = 0
for k in sorted(cited & bibkeys):
    typ, block = entries[k]
    miss = [fld for fld in ("author", "title", "year") if not has_field(block, fld)]
    if miss:
        print(f"   - {k} ({typ}): missing {miss}")
        bad += 1
if not bad:
    print("   none")
