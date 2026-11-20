"""The little these tools share: -h/--help, and a check that the arguments
they need were given, so a missing one is a usage line rather than a crash
(or, worse, a folder named --help)."""
import sys


def check(doc: str, need: int = 0) -> None:
    args = sys.argv[1:]
    if any(a in ("-h", "--help") for a in args):
        print((doc or "").strip())
        sys.exit(0)
    if len(args) < need or any(a.startswith("-") for a in args):
        print((doc or "").strip(), file=sys.stderr)
        sys.exit(f"\n✗ {sys.argv[0]} needs {need} argument{'s' if need != 1 else ''} "
                 "(see above)" if len(args) < need else f"\n✗ unknown option in {args}")
