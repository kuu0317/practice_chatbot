# チャットボット開発課題

この課題では、OpenAI API・データベース・フロントエンドを組み合わせたチャットボットシステムのスケルトンコードをもとに、各種機能を自分で実装してもらいます。

## 目的
- API連携・DB操作・UI/UXの基礎を実践的に学ぶ
- バックエンドとフロントエンドの連携を体験する

## 課題内容

### 1. OpenAI APIを叩く
- `backend/app/services/ai_client.py` の `generate_reply` メソッド内の `TODO` を実装し、OpenAI APIからAI応答を取得できるようにしてください。
- [公式ドキュメント](https://platform.openai.com/docs/api-reference/chat/create) を参考に、APIリクエスト・レスポンス処理を行ってください。

### 2. DBを構築・起動
- `backend/app/db.py` の `init_db_with_retry` などの `TODO` を実装し、DBの初期化・テーブル作成を行ってください。
- `backend/app/models.py` の `ChatMessage` モデルを定義してください。

#### 2-1. DB操作（CRUD）
- `backend/app/repositories/history.py` の各CRUD関数（`create_message` など）の `TODO` を実装してください。

#### 2-2. ChatBotにDB適用（履歴参照）
- `backend/app/routers/chat.py` の `TODO` 箇所を実装し、チャット履歴の保存・取得・編集・削除がDB経由でできるようにしてください。

### 3. フロントエンド：リセットボタンの実装
- `frontend/src/App.tsx` のリセットボタンの `TODO` を実装し、履歴削除APIと連携できるようにしてください。
- `frontend/src/api.ts` の `deleteHistory` 関数も実装してください。

## 進め方
- 各 `TODO` 箇所には「ガイドコメント」が付いています。順番に実装してください。
- わからない用語や技術は公式ドキュメントやネットで調べてみましょう。
- 動作確認は `docker compose up` で全体を起動し、フロントエンド（http://localhost:5173）から行えます。

## 完了の目安
- チャット送信・AI応答・履歴保存/取得/編集/削除・リセットボタンがすべて動作すればOKです。

## 補足
- バックエンドはFastAPI、フロントエンドはReact+TypeScriptです。
- 質問やエラーがあれば、講師やメンターに相談してください。

---

頑張って取り組んでください！
