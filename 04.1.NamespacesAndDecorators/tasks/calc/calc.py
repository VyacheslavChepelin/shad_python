import sys
import math
from typing import Any

PROMPT = '>>> '


def run_calc(context: dict[str, Any] | None = None) -> None:
    """Run interactive calculator session in specified namespace"""
    namespace = context.copy() if context is not None else {}
    namespace['__builtins__'] = {}
    while True:
        print(PROMPT, end='')
        line = sys.stdin.readline()
        if not line:
            break
        print(eval(line, namespace), end="\n")
    print('')



if __name__ == '__main__':
    context = {'math': math}
    run_calc(context)
