import sys
from utilities import run_migration

if __name__ == '__main__':
    if len(sys.argv) == 3:
        project_key = sys.argv[1]
        dry_run: bool = sys.argv[2].lower() in ["true", "t", "1"] if sys.argv[2] is not None else False
        print(f"Project key: {project_key} Dry Run: {dry_run}")
        run_migration(project_key, dry_run)
    elif len(sys.argv) == 2:
        project_key = sys.argv[1]
        print(f"Project key: {project_key} Dry Run: {False}")
        run_migration(project_key, False)
    else:
        print("{project_key} are require")
