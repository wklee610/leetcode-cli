

def _req_problem_variable(
    mode: str,
    difficulty: str | None,
    start: int
) -> dict:
    filters = {}
    if mode == "solved":
        filters["status"] = "AC"
    elif mode == "unsolved":
        filters["status"] = "NOT_STARTED"
    elif mode == "tried":
        filters["status"] = "TRIED"

    if difficulty in ("easy", "medium", "hard"):
        filters["difficulty"] = difficulty.upper()

    return {
        "categorySlug": "",
        "limit": 10,
        "skip": start,
        "filters": filters
    }


def _req_one_problem_variable(
    problem_id
) -> dict:
    return {
        "categorySlug": "",
        "limit": 1,
        "skip": problem_id - 1,
        "filters": {}
    }
def _req_problem_detail_variable(
    titleSlug
) -> dict:
    return {
        "titleSlug": titleSlug
    }

def _req_problem_submit_variable(
    language,
    code,
    problem_id
):
    language = language.lower()
    return {
        "lang": language,
        "typed_code": code,
        "question_id": problem_id
    }

def _req_problem_solution_detail_variable(
    submission_id
):
    return {
        "submissionId": submission_id
    }

def _req_user_progress_variable(
    user_name
):
    return {
        "userSlug": user_name
    }