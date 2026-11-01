import argparse
import json
import os
from .simulator import generate_readings
from .storage import WaterStore
from .service import WaterService


def main():
    parser = argparse.ArgumentParser(description="Water-treatment monitoring demo utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    seed = sub.add_parser("seed", help="Insert synthetic demo telemetry into SQLite")
    seed.add_argument("--count", type=int, default=200)
    seed.add_argument("--clear", action="store_true")
    args = parser.parse_args()
    store = WaterStore(os.getenv("WATER_DB_PATH", "./data/water_plant.db"))
    if args.command == "seed":
        if args.clear:
            store.clear()
        service = WaterService(store)
        alarm_count = 0
        for reading in generate_readings(args.count):
            result = service.ingest(reading)
            alarm_count += len(result["alarms"])
        print(json.dumps({"inserted": args.count, "alarms_generated": alarm_count, "database": store.db_path}, indent=2))


if __name__ == "__main__":
    main()
