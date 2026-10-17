import json
import sys

from .task_compiler import compile_task


def main():
    spec = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(compile_task(spec), indent=2))


if __name__ == "__main__":
    main()
