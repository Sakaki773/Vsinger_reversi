import sys


def self_check_imports() -> None:
    import tkinter  # noqa: F401
    import core  # noqa: F401
    import tk_ui  # noqa: F401


def main() -> None:
    if "--self-check-imports" in sys.argv:
        self_check_imports()
        return

    from tk_ui import run_app

    run_app()


if __name__ == "__main__":
    main()
