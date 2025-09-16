# OpenAI APIを利用したAIクライアント
import asyncio, httpx
from typing import Tuple, Optional, List, Dict
from ..config import OPENAI_API_KEY, AI_MODEL, MAX_TOKENS_OUTPUT, OPENAI_DRYRUN

# レートリミット時の例外
class AIRateLimitError(Exception): ...
# 上流APIエラー時の例外
class AIUpstreamError(Exception): ...

# OpenAI APIクライアント
class AIClient:
    def __init__(self, api_key: Optional[str] = OPENAI_API_KEY, model: Optional[str] = AI_MODEL):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"

    # ユーザー入力・履歴からAI応答を生成
    async def generate_reply(
        self,
        message: str,
        system: Optional[str],
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[str, int, int]:
        if OPENAI_DRYRUN:
            return "[DRYRUN応答] こんにちは！", 0, 0

        # TODO: OpenAI APIを呼び出してAIの応答を取得してください。
        # --- ガイド ---
    # 1. self.api_key, self.model, message, system, history を使ってAPIリクエスト用のデータを作成します。
    # 2. httpx.AsyncClient などで https://api.openai.com/v1/chat/completions にPOSTリクエストを送ります。
    # 3. レスポンスから reply, prompt_tokens, completion_tokens を取り出して return してください。
    # 4. エラー時は例外を投げてください（例: raise AIUpstreamError("...")）
    # 5. 公式ドキュメント: https://platform.openai.com/docs/api-reference/chat/create