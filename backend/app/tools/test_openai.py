# OpenAI APIの疎通テスト用スクリプト
import sys, asyncio
from ..services.ai_client import AIClient

# メッセージを送信しAI応答を表示
async def main():
    msg = "Hello from test script" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    client = AIClient()
    reply, tok_in, tok_out = await client.generate_reply(msg, system=None, history=None)
    print("reply:", reply)
    print("usage:", {"input": tok_in, "output": tok_out})

if __name__ == "__main__":
    asyncio.run(main())