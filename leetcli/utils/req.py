LEETCODE_PROBLEMS_URL = "https://leetcode.com/problems/"

def _req_header(csrftoken) -> dict:
    return {
            "Content-Type": "application/json",
            "Referer": LEETCODE_PROBLEMS_URL,
            "User-Agent": "Mozilla/5.0",
            "x-csrftoken": csrftoken
        }

def _req_cookies(session, csrftoken) -> dict:
        return {
            "LEETCODE_SESSION": session,
            "csrftoken": csrftoken
        }

def _req_solution_header(csrftoken, titleSlug) -> dict:
      return {
        "x-csrftoken": csrftoken,
        "referer": f"{LEETCODE_PROBLEMS_URL}{titleSlug}/",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "origin": "https://leetcode.com",
    }
