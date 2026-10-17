"""CLI: python -m src.policy_builder_cli {build,diff,validate,show}"""

import argparse, importlib, json, sys
from pathlib import Path
from . import policy_builder as pb


def _load_rules():
    spec = importlib.util.spec_from_file_location("policy_source", "data/policy_source.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.RULES, mod.DEFAULT


def main(argv=None):
    ap = argparse.ArgumentParser(prog="policy")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    d = sub.add_parser("diff")
    d.add_argument("other")
    sub.add_parser("validate")
    sub.add_parser("show")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        rules, default = _load_rules()
        pol = pb.build(rules, default=default)
        h = pb.write(pol)
        print(f"wrote data/policy.json  sha256={h}  rules={len(rules)}  default={default}")
    elif a.cmd == "diff":
        print(json.dumps(pb.diff("data/policy.json", a.other), indent=2))
    elif a.cmd == "validate":
        rules, default = _load_rules()
        try:
            pb.build(rules, default=default)
            print("ok")
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
    elif a.cmd == "show":
        print(Path("data/policy.json").read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
