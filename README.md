# Atendee Statistics Memo
このソフトウェアは、

## 要件
Python 3 がインストールされていること。本ソフトウェアは Python 3.11 で動作確認しました。

## 構築
必要なパッケージを pip でインストールします。動作環境として使用する仮想環境 (venv) を
作成することを推奨します。

```
$ pip install -r requirements.txt
```

以下のコマンドでデータベースを作成します。

```
$ python createdb.py
```

カレントディレクトリにデータベースファイル attendee.db が作られます。

## 起動
以下のコマンドで起動します。

```
$ streamlit run app.py
```

終了するときは、起動したターミナルで Ctrl-C を入力します。