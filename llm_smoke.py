"""Call each model configured in main.py once (no Metaculus access, nothing published)."""
import asyncio
import sys

import dotenv

dotenv.load_dotenv()

from main import build_llms  # noqa: E402


async def main() -> int:
    failures = 0
    for purpose, llm in build_llms().items():
        try:
            reply = await llm.invoke("Reply with the single word OK if you can read this.")
            print(f"PASS {purpose} {llm.model}: {reply.strip()[:80]!r}")
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"FAIL {purpose} {llm.model}: {type(error).__name__}: {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
