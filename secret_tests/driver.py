import importlib.util
import datetime
import os

def test_student_code(solution_path):
    report_dir = os.path.dirname(solution_path)
    report_path = os.path.join(report_dir, "report.txt")
    report_lines = [f"=== Traffic Control System Test Run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="]

    spec = importlib.util.spec_from_file_location("student_module", solution_path)
    student_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(student_module)
    Analyzer = student_module.TrafficControlSystem

    randomized_failures = set()

    # Anti-cheat check: per method isolation

    # 1. add_intersection
    try:
        rand1 = Analyzer()
        rand1.add_intersection("TestX", 77)
        if rand1.traffic_data.get("TestX") != 77:
            randomized_failures.add("add_intersection")
    except:
        randomized_failures.add("add_intersection")

    # 2. update_vehicle_count
    try:
        rand2 = Analyzer()
        rand2.traffic_data = {"X": 15}
        rand2.update_vehicle_count("X", 100)
        if rand2.traffic_data.get("X") != 100:
            randomized_failures.add("update_vehicle_count")
    except:
        randomized_failures.add("update_vehicle_count")

    # 3. get_congested_intersections
    try:
        rand3 = Analyzer()
        rand3.traffic_data = {"X": 100, "Y": 90, "Z": 40}
        congested = rand3.get_congested_intersections(50)
        expected = {"X": 100, "Y": 90}
        if not all(k in congested and congested[k] == v for k, v in expected.items()):
            randomized_failures.add("get_congested_intersections")
    except:
        randomized_failures.add("get_congested_intersections")

    # 4. adjust_traffic_signals — test in isolation from other functions
    try:
        rand4 = Analyzer()
        rand4.traffic_data = {
            "X": 100,  # should be Long Green
            "Y": 90,   # should be Long Green
            "Z": 40,   # should be Normal Green
            "W": 55    # should be Normal Green
        }
        signals = rand4.adjust_traffic_signals()
        expected = {
            "X": "Long Green",
            "Y": "Long Green",
            "Z": "Normal Green",
            "W": "Normal Green"
        }
        if not all(k in signals and signals[k] == v for k, v in expected.items()):
            randomized_failures.add("adjust_traffic_signals")
    except:
        randomized_failures.add("adjust_traffic_signals")

    # === MAIN TEST CASES ===
    test_cases = [
        ("Visible", "Add Intersection", "add_intersection", ("5th Avenue & Main St", 20), {"5th Avenue & Main St": 20}),
        ("Visible", "Update Vehicle Count", "update_vehicle_count", ("5th Avenue & Main St", 35), {"5th Avenue & Main St": 35}),
        ("Visible", "Get Congested Intersections", "get_congested_intersections", (30,), {"5th Avenue & Main St": 35}),
        ("Hidden", "Adjust Traffic Signals", "adjust_traffic_signals", (), {
            "5th Avenue & Main St": "Long Green",
            "Broadway & 1st St": "Normal Green",
            "Central Square": "Short Green"
        }),
        ("Hidden", "Update Non-Existent Intersection", "update_vehicle_count", ("Unknown", 50), "Error: Intersection not found")
    ]

    for i, (section, desc, func, args, expected) in enumerate(test_cases, 1):
        try:
            analyzer = Analyzer()

            # Setup specific initial state
            if func == "add_intersection":
                analyzer.traffic_data = {}
            elif func == "update_vehicle_count" and "Unknown" in args:
                analyzer.traffic_data = {}
            elif func == "get_congested_intersections":
                analyzer.traffic_data = {"5th Avenue & Main St": 35}
            elif func == "adjust_traffic_signals":
                analyzer.traffic_data = {
                    "5th Avenue & Main St": 85,
                    "Broadway & 1st St": 50,
                    "Central Square": 25
                }
            else:
                analyzer.traffic_data = {"5th Avenue & Main St": 20}

            method = getattr(analyzer, func)
            result = method(*args) if args else method()

            if func in randomized_failures:
                msg = f"❌ {section} Test Case {i} Failed due to randomized logic failure for {func}"
            else:
                passed = False
                if isinstance(result, dict) and isinstance(expected, dict):
                    passed = all(k in result and result[k] == v for k, v in expected.items()) and \
                             all(k in expected and expected[k] == v for k, v in result.items())
                else:
                    passed = result == expected

                if not passed and expected == "Error: Intersection not found":
                    passed = result == "Error: Intersection not found"

                msg = f"✅ {section} Test Case {i} Passed: {desc}" if passed else \
                      f"❌ {section} Test Case {i} Failed: {desc} | Expected={expected}, Got={result}"

        except Exception as e:
            msg = f"❌ {section} Test Case {i} Crashed: {desc} | Error: {str(e)}"

        print(msg)
        report_lines.append(msg)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

if __name__ == "__main__":
    student_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "student_workspace", "solution.py"))
    test_student_code(student_path)
