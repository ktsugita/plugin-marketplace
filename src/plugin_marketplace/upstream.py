"""upstream.toml に書かれた Gist から、上流のスキルを取得して上書きする。"""

import json
import re
import tomllib
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

GIST_API = "https://api.github.com/gists/{gist_id}"


@dataclass(frozen=True)
class Gist:
    revision: str
    content: str


Fetch = Callable[[str, str], Gist]


def update_upstream(root: Path, fetch: Fetch) -> None:
    toml_path = root / "upstream.toml"
    text = toml_path.read_text(encoding="utf-8")
    # 1つでも失敗したら何も書かないよう、書き込みの前に、取得と upstream.toml の書き換えを済ませる。
    fetched = [
        (source, fetch(source["gist"], source["file"])) for source in tomllib.loads(text)["sources"]
    ]
    new_text = text
    for source, gist in fetched:
        new_text = _with_revision(new_text, source["gist"], gist.revision)
    if [s.get("revision") for s in tomllib.loads(new_text)["sources"]] != [
        gist.revision for _, gist in fetched
    ]:
        raise RuntimeError("upstream.toml の revision を更新できなかった。revision の行を確かめる")
    for source, gist in fetched:
        content = gist.content.replace("\r\n", "\n").rstrip("\n") + "\n"
        (root / source["dest"]).write_text(content, encoding="utf-8", newline="\n")
    toml_path.write_text(new_text, encoding="utf-8", newline="\n")


def _with_revision(text: str, gist_id: str, revision: str) -> str:
    """gist_id を持つ [[sources]] のブロックの revision の行だけを置き換える。"""
    blocks = re.split(r"(?m)^(?=\[\[sources\]\])", text)
    gist_line = re.compile(rf'(?m)^gist\s*=\s*"{re.escape(gist_id)}"')
    revision_line = re.compile(r'(?m)^(revision\s*=\s*)"[^"]*"')
    return "".join(
        revision_line.sub(lambda m: f'{m.group(1)}"{revision}"', block)
        if gist_line.search(block)
        else block
        for block in blocks
    )


def fetch_gist(gist_id: str, file: str) -> Gist:
    """公開 Gist の最新の版から、file の内容とリビジョンを取得する。認証は使わない。"""
    request = urllib.request.Request(
        GIST_API.format(gist_id=gist_id),
        headers={"Accept": "application/vnd.github+json", "User-Agent": "plugin-marketplace"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    entry = data["files"].get(file)
    if entry is None:
        raise RuntimeError(f"Gist {gist_id} に {file} がありません")
    if entry.get("truncated"):
        raise RuntimeError(f"Gist {gist_id} の {file} が大きすぎて、API が内容を切り詰めました")
    return Gist(revision=data["history"][0]["version"], content=entry["content"])


def main() -> None:
    update_upstream(Path.cwd(), fetch_gist)
    print("upstream.toml と配置先を更新した。変更は git diff で確認する。")


if __name__ == "__main__":
    main()
