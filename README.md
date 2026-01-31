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

### 2.Windows exe版
1.Releases から BDSAutoBackup.exe をダウンロード

2.exe をダブルクリックで起動

3.上記と同様に GUI で設定して使用

## バックアップ保存先
-  デフォルトは `backups/` フォルダに zip 形式で保存
-  古いバックアップは最大世代数を超えると自動削除
-  復元は「Actions」タブの Restore Backup から選択してワンクリック

## 注意
-  サーバーが起動中の場合、ワールド保存コマンドを送信するため、save hold → save resume が動作します
-  バックアップ中はファイルコピーが多くなるため、重いサーバーや大きなワールドでは時間がかかることがあります
-  復元前に .restore_backup/ に現在のデータを退避するので、万が一失敗しても元に戻せます

## 配布内容

```
BDSAutoBackup/
 ├─ BDSAutoBackup.py        ← Pythonスクリプト版
 ├─ backup_config.json       ← 設定ファイル初期版
 ├─ backups/                ← バックアップ保存先（自動作成）
 └─ README.md               ← README
```

## 作者

- 作成: Takkunlego0916(TakkunMCJP)
- Discord: takkun_mc_jp
