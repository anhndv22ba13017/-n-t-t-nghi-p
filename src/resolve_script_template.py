from pathlib import Path


def build_template(plan_path: Path) -> str:
    return f"""# DaVinci Resolve import template
# Replace this template with your actual Resolve environment and API calls.

from pathlib import Path
import json

PLAN_PATH = Path(r"{plan_path}")


def main():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    print("Project:", plan["project_name"])
    print("Timeline:", plan["timeline_name"])
    print("Clip count:", len(plan["clips"]))
    print("Next: connect this script to DaVinci Resolve scripting API")


if __name__ == "__main__":
    main()
"""

