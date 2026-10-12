"""`astromesh-okf`: serve a bundle over MCP, or inspect it from the terminal."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from astromesh_okf import __version__
from astromesh_okf.tools import OKFTools


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="astromesh-okf", description=__doc__)
    parser.add_argument("--version", action="version", version=f"astromesh-okf {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)
    mcp = sub.add_parser("mcp", help="serve the bundle's tools over MCP (stdio)")
    mcp.add_argument("bundle")
    mcp.add_argument("--prefix", default="")
    idx = sub.add_parser("index", help="print a directory index")
    idx.add_argument("bundle")
    idx.add_argument("path", nargs="?", default="/")
    rd = sub.add_parser("read", help="print one concept as JSON")
    rd.add_argument("bundle")
    rd.add_argument("concept_id")
    fd = sub.add_parser("find", help="search concepts, print JSON")
    fd.add_argument("bundle")
    fd.add_argument("--text")
    fd.add_argument("--type")
    fd.add_argument("--tag", action="append", dest="tags")
    fd.add_argument("--include-deprecated", action="store_true")
    fd.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    if not Path(args.bundle).is_dir():
        print(f"astromesh-okf: not a directory: {args.bundle}", file=sys.stderr)
        return 2
    if args.cmd == "mcp":
        from astromesh_okf.mcp import build_server

        try:
            server = build_server(args.bundle, prefix=args.prefix)
        except ImportError as exc:
            print(f"astromesh-okf: {exc}", file=sys.stderr)
            return 2
        server.run()
        return 0
    tools = OKFTools(args.bundle)
    if args.cmd == "index":
        print(tools.kb_index(args.path))
    elif args.cmd == "read":
        print(tools.kb_read(args.concept_id))
    else:
        print(tools.kb_find(args.text, args.type, args.tags, args.include_deprecated, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
