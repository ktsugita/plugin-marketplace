from pathlib import Path

import pytest

from plugin_marketplace.upstream import Gist, update_upstream

OLD_REVISION = "a" * 40
NEW_REVISION = "b" * 40

ALPHA_DEST = "plugins/writing/skills/alpha/SKILL.md"
BETA_DEST = "plugins/writing/skills/beta/SKILL.md"

UPSTREAM_TOML = f"""\
# 上流から取り込むスキル。update_upstream が revision を更新する。

[[sources]]
skill = "alpha"
gist = "gist-alpha"
revision = "{OLD_REVISION}"
file = "SKILL.md"
dest = "{ALPHA_DEST}"
"""

TWO_SOURCES_TOML = (
    UPSTREAM_TOML
    + f"""
[[sources]]
skill = "beta"
gist = "gist-beta"
revision = "{OLD_REVISION}"
file = "SKILL.md"
dest = "{BETA_DEST}"
"""
)


def make_repo(
    tmp_path: Path, toml: str = UPSTREAM_TOML, dests: tuple[str, ...] = (ALPHA_DEST,)
) -> Path:
    (tmp_path / "upstream.toml").write_text(toml, encoding="utf-8", newline="\n")
    for dest in dests:
        path = tmp_path / dest
        path.parent.mkdir(parents=True)
        path.write_text("古い内容\n", encoding="utf-8", newline="\n")
    return tmp_path


def test_取得した内容を末尾の改行1つで配置先に書く(tmp_path: Path) -> None:
    root = make_repo(tmp_path)

    def fetch(gist_id: str, file: str) -> Gist:
        return Gist(revision=NEW_REVISION, content="# 見出し\n\n本文")

    update_upstream(root, fetch)

    assert (root / ALPHA_DEST).read_bytes() == "# 見出し\n\n本文\n".encode()


def test_取得した内容の改行はLFにそろえて書く(tmp_path: Path) -> None:
    root = make_repo(tmp_path)

    def fetch(gist_id: str, file: str) -> Gist:
        return Gist(revision=NEW_REVISION, content="一行目\r\n二行目\r\n")

    update_upstream(root, fetch)

    assert (root / ALPHA_DEST).read_bytes() == "一行目\n二行目\n".encode()


def test_upstream_tomlはrevisionの行だけを更新する(tmp_path: Path) -> None:
    root = make_repo(tmp_path)

    def fetch(gist_id: str, file: str) -> Gist:
        return Gist(revision=NEW_REVISION, content="本文")

    update_upstream(root, fetch)

    assert (root / "upstream.toml").read_text(encoding="utf-8") == UPSTREAM_TOML.replace(
        OLD_REVISION, NEW_REVISION
    )


def test_等号の前後に空白がない書式でもrevisionを更新する(tmp_path: Path) -> None:
    toml = UPSTREAM_TOML.replace(" = ", "=")
    root = make_repo(tmp_path, toml)

    def fetch(gist_id: str, file: str) -> Gist:
        return Gist(revision=NEW_REVISION, content="本文")

    update_upstream(root, fetch)

    assert (root / "upstream.toml").read_text(encoding="utf-8") == toml.replace(
        OLD_REVISION, NEW_REVISION
    )


def test_revisionを更新できないときは何も変更せずエラーにする(tmp_path: Path) -> None:
    toml = UPSTREAM_TOML.replace(f'revision = "{OLD_REVISION}"\n', "")
    root = make_repo(tmp_path, toml)

    def fetch(gist_id: str, file: str) -> Gist:
        return Gist(revision=NEW_REVISION, content="新しい内容")

    with pytest.raises(RuntimeError, match="revision"):
        update_upstream(root, fetch)

    assert (root / ALPHA_DEST).read_text(encoding="utf-8") == "古い内容\n"
    assert (root / "upstream.toml").read_text(encoding="utf-8") == toml


def test_同じ内容を続けて取得しても何も変わらない(tmp_path: Path) -> None:
    root = make_repo(tmp_path)

    def fetch(gist_id: str, file: str) -> Gist:
        return Gist(revision=NEW_REVISION, content="本文")

    update_upstream(root, fetch)
    after_first = ((root / ALPHA_DEST).read_bytes(), (root / "upstream.toml").read_bytes())
    update_upstream(root, fetch)

    assert ((root / ALPHA_DEST).read_bytes(), (root / "upstream.toml").read_bytes()) == after_first


def test_取得に1つでも失敗したら何も変更しない(tmp_path: Path) -> None:
    root = make_repo(tmp_path, TWO_SOURCES_TOML, (ALPHA_DEST, BETA_DEST))

    def fetch(gist_id: str, file: str) -> Gist:
        if gist_id == "gist-beta":
            raise RuntimeError("取得に失敗した")
        return Gist(revision=NEW_REVISION, content="新しい内容")

    with pytest.raises(RuntimeError):
        update_upstream(root, fetch)

    assert (root / ALPHA_DEST).read_text(encoding="utf-8") == "古い内容\n"
    assert (root / BETA_DEST).read_text(encoding="utf-8") == "古い内容\n"
    assert (root / "upstream.toml").read_text(encoding="utf-8") == TWO_SOURCES_TOML
