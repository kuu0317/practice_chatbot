import asyncio, httpx
from typing import Tuple, Optional, List, Dict
from ..config import OPENAI_API_KEY, AI_MODEL

class AIRateLimitError(Exception): ...
class AIUpstreamError(Exception): ...

class AIClient:
    def __init__(self, api_key: Optional[str] = OPENAI_API_KEY, model: Optional[str] = AI_MODEL):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"

    async def generate_reply(
        self,
        message: str,
        system: Optional[str],
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[str, int, int]:
        if not self.api_key:
            raise AIUpstreamError("OPENAI_API_KEY missing")

        msgs: List[Dict[str,str]] = []
        if system:
            msgs.append({"role": "system", "content": system})
        for h in (history or []):
            if h.get("role") in ("user","assistant") and h.get("text"):
                msgs.append({"role": h["role"], "content": h["text"]})
        msgs.append({"role": "user", "content": message})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "messages": msgs}

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=20) as client:
                    r = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers, json=payload
                    )
                if r.status_code == 429:
                    if attempt < 2:
                        await asyncio.sleep(0.5 * (2 ** attempt)); continue
                    raise AIRateLimitError("rate limited")
                if r.status_code >= 500:
                    if attempt < 2:
                        await asyncio.sleep(0.5 * (2 ** attempt)); continue
                    raise AIUpstreamError("upstream error")
                r.raise_for_status()
                data = r.json()
                reply = data["choices"][0]["message"]["content"]
                usage = data.get("usage") or {}
                return reply, int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
            except httpx.TimeoutException as e:
                if attempt < 2:
                    await asyncio.sleep(0.5 * (2 ** attempt)); continue
                raise AIUpstreamError("timeout") from e
            except httpx.HTTPStatusError as e:
                raise AIUpstreamError(str(e)) from e

        raise AIUpstreamError("unexpected failure")