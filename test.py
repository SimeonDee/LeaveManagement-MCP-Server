import main
from pprint import PrettyPrinter

printer = PrettyPrinter(indent=3)

if __name__ == "__main__":
    printer.pprint(main.employees)
    printer.pprint(main.register_employee("Bolatito"))
    printer.pprint(
        main.apply_for_leave(
            "0001",
            ["2025-07-20", "2025-07-21", "2025-07-22"],
            "vacation",
        )
    )
    printer.pprint(main.employees)
