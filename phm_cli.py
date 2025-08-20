# phm_cli.py
import argparse
from phm_runner import run_test
from utils.report import generate_html
from db.db_utils import init_db

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    runp = sub.add_parser("run")
    runp.add_argument("--test", required=True)
    runp.add_argument("--engine", default="mock")
    runp.add_argument("--dry-repair", action="store_true")

    sub.add_parser("initdb")
    rep = sub.add_parser("report")
    rep.add_argument("--out", default="reports/report.html")

    args = parser.parse_args()
    if args.cmd == "run":
        res = run_test(args.test, engine=args.engine, dry_run_repair=args.dry_repair)
        print(res)
    elif args.cmd == "initdb":
        init_db()
    elif args.cmd == "report":
        path = generate_html(args.out)
        print("Report written to", path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
