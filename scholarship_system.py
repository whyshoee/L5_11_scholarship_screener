"""Student scholarship eligibility screener.

Computes a merit score from GPA and extracurricular credits, checks family
income against a limit, and saves the shortlist to ``scholarships.json``.
"""
import ast
import json
import operator

RESULTS = {}
CONFIG = {"formula": "gpa * 10 + credits * 2"}
INCOME_LIMIT = 800000
CUTOFF = 85
MAX_GPA = 10.0

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def _eval_node(node, variables):
    """Evaluate a parsed arithmetic expression without using eval()."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, variables)
    if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](
            _eval_node(node.left, variables),
            _eval_node(node.right, variables),
        )
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_node(node.operand, variables)
    raise ValueError("Unsupported element in merit formula")

def calculate_merit_score(gpa, extra_credits, formula=None):
    """Return the merit score using only +, -, *, / on gpa and credits."""
    formula = formula or CONFIG["formula"]
    try:
        tree = ast.parse(formula, mode="eval")
        return _eval_node(tree, {"gpa": gpa, "credits": extra_credits})
    except (SyntaxError, ZeroDivisionError) as err:
        raise ValueError(f"Invalid merit formula: {err}") from err

def validate_scores(test_scores):
    """Raise ValueError if the applicant data is missing or out of range."""
    gpa = test_scores.get("gpa")
    extra_credits = test_scores.get("credits", 0)
    income = test_scores.get("income")
    if gpa is None or not 0 <= gpa <= MAX_GPA:
        raise ValueError(f"GPA must be between 0 and {MAX_GPA}")
    if extra_credits < 0:
        raise ValueError("Credits cannot be negative")
    if income is None or income < 0:
        raise ValueError("Income is missing or negative")
    return gpa, extra_credits, income

def evaluate_applicant(student_id, test_scores, logs=None):
    """Score one applicant, store the result and return eligibility."""
    if logs is None:
        logs = []
    gpa, extra_credits, income = validate_scores(test_scores)
    score = calculate_merit_score(gpa, extra_credits)
    eligible = score >= CUTOFF and income < INCOME_LIMIT
    RESULTS[student_id] = {"score": score, "eligible": eligible}
    logs.append(f"{student_id} scored {score}")
    return eligible

def change_formula(new_formula):
    """Replace the merit formula after checking that it is valid."""
    calculate_merit_score(1, 1, new_formula)
    CONFIG["formula"] = new_formula

def persist_results(file="scholarships.json"):
    """Save all results to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(RESULTS, handle)

def load_results(file="scholarships.json"):
    """Load results from a JSON file, if it exists and is valid."""
    try:
        with open(file, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as err:
        print(f"Could not load results: {err}")
        return
    RESULTS.clear()
    RESULTS.update(data)

def print_shortlist():
    """Print every eligible applicant."""
    print("Shortlisted applicants:")
    for student_id, record in RESULTS.items():
        if record["eligible"]:
            print(" ", student_id, "score =", record["score"])

def safe_evaluate(student_id, test_scores):
    """Evaluate an applicant, reporting invalid data instead of crashing."""
    try:
        evaluate_applicant(student_id, test_scores)
    except ValueError as err:
        print(f"Skipped {student_id}: {err}")

def main():
    """Run the demo screening."""
    safe_evaluate("U001", {"gpa": 9.1, "credits": 4, "income": 450000})
    safe_evaluate("U002", {"gpa": 7.2, "credits": 1, "income": 300000})
    safe_evaluate("U003", {"gpa": 12.5, "credits": -3, "income": -1})
    safe_evaluate("U004", {"gpa": 6.5})
    formula = input("Merit formula (Enter to keep default): ")
    if formula:
        try:
            change_formula(formula)
        except ValueError as err:
            print(f"{err}. Keeping the default formula.")
    safe_evaluate("U005", {"gpa": 8.4, "credits": 3, "income": 600000})
    persist_results()
    load_results()
    print_shortlist()

if __name__ == "__main__":
    main()
