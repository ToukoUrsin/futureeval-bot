"""Call each model configured in main.py once (no Metaculus access, nothing published)."""
import asyncio
import ast
import sys

from forecasting_tools import GeneralLlm


def configured_llms() -> dict[str, dict]:
    tree = ast.parse(open("main.py").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "llms" and isinstance(node.value, ast.Dict):
            out = {}
            for k, v in zip(node.value.keys, node.value.values):
                kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in v.keywords}
                out[ast.literal_eval(k)] = kwargs
            return out
    raise SystemExit("no llms= block found in main.py")


async def main() -> int:
    failures = 0
    for purpose, kwargs in configured_llms().items():
        try:
            reply = await GeneralLlm(**kwargs).invoke(
                "Reply with the single word OK if you can read this."
            )
            print(f"PASS {purpose} {kwargs['model']}: {reply.strip()[:80]!r}")
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"FAIL {purpose} {kwargs['model']}: {type(error).__name__}: {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
