#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

tmpdir=$(make_tmpdir)

sync_codex_mirror() {
  local repo="$1"
  rm -rf "$repo/plugins/waza/skills" "$repo/plugins/waza/rules"
  cp -R "$repo/skills" "$repo/plugins/waza/skills"
  cp -R "$repo/rules" "$repo/plugins/waza/rules"
}

# Case 1: missing closing frontmatter delimiter.
copy_repo "$tmpdir/repo"
version=$(cat "$tmpdir/repo/VERSION")
(cd "$tmpdir/repo" && python3 -S scripts/verify_skills.py --root . >"$tmpdir/no-site.out")
grep -q "all versions in lock-step with VERSION=$version" "$tmpdir/no-site.out"
python3 -c "
from pathlib import Path
p = Path('$tmpdir/repo/skills/check/SKILL.md')
t = p.read_text()
t = t.replace('---\n', '', 1)
i = t.find('\n---\n')
p.write_text(t[:i] + t[i+5:])
"
if (cd "$tmpdir/repo" && python3 scripts/verify_skills.py --root . >"$tmpdir/frontmatter.out" 2>"$tmpdir/frontmatter.err"); then
  echo "verify-skills should reject missing frontmatter delimiters"; exit 1
fi
grep -q 'INVALID FRONTMATTER' "$tmpdir/frontmatter.err"

# Case 2: marketplace lists a skill that has no directory.
copy_repo "$tmpdir/repo2"
python3 -c "
import json
p = '$tmpdir/repo2/.claude-plugin/marketplace.json'
d = json.load(open(p))
d['plugins'].append({'name':'waza-ghost','description':'x','version':'1.0.0','category':'development','source':'./skills/ghost','homepage':'https://example.com'})
open(p,'w').write(json.dumps(d, indent=2) + '\n')
"
if (cd "$tmpdir/repo2" && python3 scripts/verify_skills.py --root . >"$tmpdir/market.out" 2>"$tmpdir/market.err"); then
  echo "verify-skills should reject marketplace-only entries"; exit 1
fi
grep -q 'MISSING SKILL DIRECTORY: ghost' "$tmpdir/market.err"

# Case 3: marketplace source path points at the wrong skill.
copy_repo "$tmpdir/repo3"
python3 -c "
import json
p = '$tmpdir/repo3/.claude-plugin/marketplace.json'
d = json.load(open(p))
for entry in d['plugins']:
    if entry['name'] == 'waza-check':
        entry['source'] = './skills/read'
open(p,'w').write(json.dumps(d, indent=2) + '\n')
"
if (cd "$tmpdir/repo3" && python3 scripts/verify_skills.py --root . >"$tmpdir/source.out" 2>"$tmpdir/source.err"); then
  echo "verify-skills should reject wrong source paths"; exit 1
fi
grep -q 'WRONG SOURCE: waza-check' "$tmpdir/source.err"

# Case 4: broken markdown link inside a SKILL.md.
copy_repo "$tmpdir/repo4"
python3 -c "
from pathlib import Path
p = Path('$tmpdir/repo4/skills/check/SKILL.md')
p.write_text(p.read_text() + '\n[broken](missing-target.md)\n')
"
sync_codex_mirror "$tmpdir/repo4"
if (cd "$tmpdir/repo4" && python3 scripts/verify_skills.py --root . >"$tmpdir/link.out" 2>"$tmpdir/link.err"); then
  echo "verify-skills should reject broken markdown links"; exit 1
fi
grep -q 'BROKEN MARKDOWN LINK' "$tmpdir/link.err"

# Case 5: RESOLVER.md references a skill directory that doesn't exist.
copy_repo "$tmpdir/repo5"
printf '\n| trigger | skills/ghost/SKILL.md |\n' >> "$tmpdir/repo5/skills/RESOLVER.md"
sync_codex_mirror "$tmpdir/repo5"
if (cd "$tmpdir/repo5" && python3 scripts/verify_skills.py --root . >"$tmpdir/resolver.out" 2>"$tmpdir/resolver.err"); then
  echo "verify-skills should reject stale RESOLVER references"; exit 1
fi
grep -q 'RESOLVER REFERENCES MISSING SKILL: ghost' "$tmpdir/resolver.err"

# Case 6: unescaped pipe in a markdown table data row.
copy_repo "$tmpdir/repo6"
printf '\n| Col1 | Col2 |\n| --- | --- |\n| a | b | c |\n' >> "$tmpdir/repo6/skills/check/SKILL.md"
sync_codex_mirror "$tmpdir/repo6"
if (cd "$tmpdir/repo6" && python3 scripts/verify_skills.py --root . >"$tmpdir/pipe.out" 2>"$tmpdir/pipe.err"); then
  echo "verify-skills should reject unescaped pipe in table data row"; exit 1
fi
grep -q 'UNESCAPED PIPE IN TABLE' "$tmpdir/pipe.err"

# Case 7: bundle version drifts away from VERSION file.
copy_repo "$tmpdir/repo7"
python3 -c "
import json
p = '$tmpdir/repo7/.claude-plugin/marketplace.json'
d = json.load(open(p))
for e in d['plugins']:
    if e['name'] == 'waza':
        e['version'] = '3.0.0'
open(p,'w').write(json.dumps(d, indent=2) + '\n')
"
if (cd "$tmpdir/repo7" && python3 scripts/verify_skills.py --root . >"$tmpdir/bundle.out" 2>"$tmpdir/bundle.err"); then
  echo "verify-skills should reject bundle version drift from VERSION"; exit 1
fi
grep -q 'VERSION DRIFT: waza bundle' "$tmpdir/bundle.err"

# Case 7b: Codex plugin version also drifts away from VERSION file.
copy_repo "$tmpdir/repo7b"
python3 -c "
import json
p = '$tmpdir/repo7b/plugins/waza/.codex-plugin/plugin.json'
d = json.load(open(p))
d['version'] = '3.0.0'
open(p,'w').write(json.dumps(d, indent=2) + '\n')
"
if (cd "$tmpdir/repo7b" && python3 scripts/verify_skills.py --root . >"$tmpdir/codex-plugin.out" 2>"$tmpdir/codex-plugin.err"); then
  echo "verify-skills should reject Codex plugin version drift from VERSION"; exit 1
fi
grep -q 'CODEX PLUGIN FIELD DRIFT' "$tmpdir/codex-plugin.err"

# Case 7c: Codex marketplace must point at the repo plugin root.
copy_repo "$tmpdir/repo7c"
python3 -c "
import json
p = '$tmpdir/repo7c/.agents/plugins/marketplace.json'
d = json.load(open(p))
d['plugins'][0]['source']['path'] = './'
open(p,'w').write(json.dumps(d, indent=2) + '\n')
"
if (cd "$tmpdir/repo7c" && python3 scripts/verify_skills.py --root . >"$tmpdir/codex-market.out" 2>"$tmpdir/codex-market.err"); then
  echo "verify-skills should reject Codex marketplace entry drift"; exit 1
fi
grep -q 'CODEX MARKETPLACE ENTRY DRIFT' "$tmpdir/codex-market.err"

# Case 8: descriptions must carry a trigger cue, not just capability prose.
copy_repo "$tmpdir/repo8"
python3 -c "
from pathlib import Path
p = Path('$tmpdir/repo8/skills/read/SKILL.md')
t = p.read_text()
t = t.replace(' Use when asked to read, fetch, quote, cite, convert, or save a URL or PDF.', '')
p.write_text(t)
"
sync_codex_mirror "$tmpdir/repo8"
if (cd "$tmpdir/repo8" && python3 scripts/verify_skills.py --root . >"$tmpdir/usewhen.out" 2>"$tmpdir/usewhen.err"); then
  echo "verify-skills should reject descriptions without Use when trigger cues"; exit 1
fi
grep -q 'DESCRIPTION MISSING USE-WHEN CUE: read' "$tmpdir/usewhen.err"

# Case 8b: public description metadata must stay English-only; multilingual
# trigger aliases belong in when_to_use.
copy_repo "$tmpdir/repo8b"
python3 -c "
from pathlib import Path
p = Path('$tmpdir/repo8b/skills/read/SKILL.md')
t = p.read_text()
t = t.replace('Use when asked to read, fetch, quote', 'Use when asked to 读一下, fetch, quote')
p.write_text(t)
"
sync_codex_mirror "$tmpdir/repo8b"
if (cd "$tmpdir/repo8b" && python3 scripts/verify_skills.py --root . >"$tmpdir/cjk-desc.out" 2>"$tmpdir/cjk-desc.err"); then
  echo "verify-skills should reject CJK in public descriptions"; exit 1
fi
grep -q 'DESCRIPTION CONTAINS CJK: read' "$tmpdir/cjk-desc.err"

# Case 9: ungrounded routing trigger inside CJK corner brackets 「」 is caught.
copy_repo "$tmpdir/repo9"
python3 -c "
from pathlib import Path
p = Path('$tmpdir/repo9/rules/waza-routing.md')
t = p.read_text()
t = t.replace('\"读一下\"', '「读一个不存在的触发词」')
p.write_text(t)
"
sync_codex_mirror "$tmpdir/repo9"
if (cd "$tmpdir/repo9" && python3 scripts/verify_skills.py --root . >"$tmpdir/routing.out" 2>"$tmpdir/routing.err"); then
  echo "verify-skills should reject ungrounded 「」 routing triggers"; exit 1
fi
grep -q 'WAZA ROUTING UNGROUNDED TRIGGER' "$tmpdir/routing.err"

echo "verify-skills smoke: ok"
