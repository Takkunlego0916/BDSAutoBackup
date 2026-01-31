# BDS Auto Backup GUI

BDS Auto Backup は、**Minecraft 統合版(Bedrock)サーバー(BDS)の自動バックアップツール**です。  
GUI で簡単に設定・操作でき、バックアップと復元を手軽に行えます。

---

## 特徴

- タブ式 GUI で設定が直感的
- 自動バックアップ（間隔設定可能）
- 手動バックアップワンクリック
- 復元機能付き（バックアップから元に戻せる）
- 古いバックアップの世代管理
- `server.properties` / `allowlist.json` / `config` などの個別ファイルもバックアップ可能
- Python 未インストールでも Windows exe で実行可能

---

## 使い方

### 1. Python版

1. Python 3.x をインストール
2. 必要ライブラリは標準のみ（追加不要）
3. リポジトリをクローンまたは ZIP を展開
4. コマンドで起動：

```bash
python BDSAutoBackup.py
```

5.GUIで以下を設定：

-  Server Executable（bedrock_server.exe のパス）

-  Working Directory（サーバーがあるフォルダ）

-  Backup Interval（秒単位）

-  Max Backups（保持する世代数）

-  Backup Targets / Extra Files（保存するフォルダやファイル）

6.「Manual Backup」で手動バックアップ、または自動バックアップが開始されます。
