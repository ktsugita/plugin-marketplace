# Domain Docs

エンジニアリング系スキルが、コードベースを調べるときに、このリポジトリのドメイン文書をどう読むかを定める。

## 調べる前に読むもの

- ルートの **`GLOSSARY.md`**。または、
- ルートに **`GLOSSARY-MAP.md`** があるときは、そちらを読む。コンテキストごとの `GLOSSARY.md` を指しているので、話題に関係するものをすべて読む。
- **`docs/adr/`**: これから作業する領域に関係する ADR を読む。multi-context のリポジトリでは、コンテキスト固有の決定として `src/<context>/docs/adr/` も確認する。

これらのファイルがなくても、**そのまま作業を進める**。ないことを指摘せず、先に作ることも提案しない。`/domain-modeling` スキル(`/grill-with-docs` と `/improve-codebase-architecture` から呼ばれる)が、用語や決定が実際に固まったときに、必要なファイルを作る。

## ファイル構成

single-context のリポジトリ(ほとんどのリポジトリ):

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

multi-context のリポジトリ(ルートに `GLOSSARY-MAP.md` がある):

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                          ← システム全体の決定
└── src/
    ├── ordering/
    │   ├── GLOSSARY.md
    │   └── docs/adr/                  ← コンテキスト固有の決定
    └── billing/
        ├── GLOSSARY.md
        └── docs/adr/
```

## 用語集の語彙を使う

出力でドメインの概念に言及するとき(Issue のタイトル、リファクタリングの提案、仮説、テスト名など)は、`GLOSSARY.md` で定義された用語を使う。用語集が `_Avoid_` として挙げている同義語は使わない。

必要な概念が用語集にまだない場合は、次のどちらかである。このプロジェクトで使わない言葉を作り出している(考え直す)か、用語集に本当に欠けている(`/domain-modeling` に伝える)。

## ADR との矛盾を示す

出力が既存の ADR と矛盾する場合は、黙って上書きせず、矛盾を明示する。

> _ADR-0007(event-sourced orders)と矛盾するが、見直す価値がある。理由は…_
