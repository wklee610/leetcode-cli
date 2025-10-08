import os
import json
import platform
from typing import (
    Optional, 
    Tuple, 
    Union
)
from http.cookiejar import CookieJar
import requests
import browser_cookie3
from tabulate import tabulate
from pathlib import Path
from leetcli.utils.req import (
    _req_header, 
    _req_cookies,
)
from leetcli.utils.query import (
    _req_user_progress_v2_query
)
from leetcli.utils.variable import (
    _req_user_progress_variable
)

LEETCODE_URL = "https://leetcode.com/graphql"
USERINFO_DIR = Path(os.path.expanduser("~/.leetcode-cli"))
USERINFO_FILE = USERINFO_DIR / "session.json"
LEETCODE_DOMAIN = "leetcode.com"


class UserInfoManager:
    def __init__(self):
        pass

    def _get_userinfo(
        self,
        url
    ) -> Optional[Tuple[str, bool]]:
        try:
            with open(USERINFO_FILE, "r") as f:
                cookies_dict = json.load(f)
            session = requests.Session()
            for k, v in cookies_dict.items():
                session.cookies.set(k, v)
            username, is_active = self._test_userinfo(url, session)
            return username, is_active
        
        except FileNotFoundError as e:
            raise e
        
        except ConnectionError as e:
            raise e
        
        except Exception as e:
            raise e

    def _create_userinfo(
        self
    ) -> Optional[Union[CookieJar, str]]:
        """
        Create New Session from Leetcode
        """
        cookies = None
        current_os = platform.system()
        browsers_support = {
            "chrome":       ["Linux", "Darwin", "Windows"],
            "firefox":      ["Linux", "Darwin", "Windows"],
            "librewolf":    ["Linux", "Darwin", "Windows"],
            "opera":        ["Linux", "Darwin", "Windows"],
            "opera_gx":     ["Darwin", "Windows"],
            "edge":         ["Linux", "Darwin", "Windows"],
            "chromium":     ["Linux", "Darwin", "Windows"],
            "brave":        ["Linux", "Darwin", "Windows"],
            "vivaldi":      ["Linux", "Darwin", "Windows"],
            "w3m":          ["Linux"],
            "lynx":         ["Linux"],
            "safari":       ["Darwin"],
        }

        for browser_name, os_list in browsers_support.items():
            if current_os not in os_list:
                continue
            try:
                func = getattr(browser_cookie3, browser_name)
            except AttributeError:
                continue

            try:
                cookies = func(domain_name="leetcode.com")
                if cookies:
                    break
            except Exception as e:
                continue
        return cookies

    def _save_userinfo(
        self, 
        cookies,
        default_language: str | None,
        LEETCODE_LANGUAGES
    ) -> None:
        dir_path = os.path.dirname(USERINFO_FILE)
        os.makedirs(dir_path, exist_ok=True)
        important_info = {}
        for cookie in cookies:
            if cookie.name in ("LEETCODE_SESSION", "csrftoken"):
                important_info[cookie.name] = cookie.value
        if default_language and LEETCODE_LANGUAGES:
            lang_key = default_language.strip().lower()
            if lang_key not in LEETCODE_LANGUAGES:
                raise ValueError(
                    f"Unsupported language: {default_language}\n"
                    f"Available options: {', '.join(sorted(set(LEETCODE_LANGUAGES.values())))}"
                )
            important_info["language"] = LEETCODE_LANGUAGES[lang_key]
        with open(USERINFO_FILE, "w") as f:
            json.dump(important_info, f, indent=2)
        
    def _test_userinfo(
        self, 
        url, 
        session
    ) -> Tuple[bool, Optional[str]]:
        try:
            headers = {
                "Referer": "https://leetcode.com/",
                "Content-Type": "application/json",
                "x-csrftoken": session.cookies.get("csrftoken"),
                "User-Agent": "Mozilla/5.0",
            }

            query = {
                "operationName": "globalData",
                "variables": {},
                "query": """
                query globalData {
                userStatus {
                    isSignedIn
                    username
                }
                }
                """
            }
            resp = session.post(url, headers=headers, json=query)
            data = resp.json()
            user_status = data.get("data", {}).get("userStatus", {})
            is_signed_in = user_status.get("isSignedIn", False)
            username = user_status.get("username")

            if is_signed_in and username:
                return True, username
            else:
                return False, None
            
        except Exception as e:
            raise ConnectionError

    def _delete_userinfo(
        self
    ) -> bool:
        try:
            if USERINFO_FILE.exists():
                USERINFO_FILE.unlink()
                return True
            else:
                return False
        except Exception as e:
            return False

    def _get_csrftoken(
        self
    ) -> str:
        with open(USERINFO_FILE, "r") as f:
            userinfo_dict = json.load(f)
        return userinfo_dict['csrftoken']

    def _get_session(
        self
    ) -> str:
        with open(USERINFO_FILE, "r") as f:
            userinfo_dict = json.load(f)
        return userinfo_dict['LEETCODE_SESSION']

    def _set_lang(
        self,
        language,
        LEETCODE_LANGUAGES
    ) -> None:
        if not USERINFO_FILE.exists():
            raise FileNotFoundError("User info file not found.")
        lang_key = language.strip().lower()
        if lang_key not in LEETCODE_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}\n"
                f"Available options: {', '.join(sorted(set(LEETCODE_LANGUAGES.values())))}"
            )
        selected_lang = LEETCODE_LANGUAGES[lang_key]
        with open(USERINFO_FILE, "r") as f:
            data = json.load(f)
        data["language"] = selected_lang

        with open(USERINFO_FILE, "w") as f:
            json.dump(data, f, indent=2)

        return selected_lang

    def _get_lang(
        self
    ) -> str:
        try:
            with open(USERINFO_FILE, "r") as f:
                userinfo_dict = json.load(f)
            return userinfo_dict['language']
        except Exception as e:
            raise FileNotFoundError("User info file not found.")
    
    def _get_user_progress(
        self,
        csrftoken,
        session,
        userinfo
    ):
        try:
            result_table = []
            headers = _req_header(csrftoken)
            cookies = _req_cookies(
                    session, 
                    csrftoken,
            )
            query = _req_user_progress_v2_query()
            variables = _req_user_progress_variable(userinfo[1])

            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": query, "variables": variables})
            )
            
            data = json.loads(response.content)
            progress_result = data["data"]["userProfileUserQuestionProgressV2"]
        
            accepted = {x["difficulty"]: x["count"] for x in progress_result["numAcceptedQuestions"]}
            failed = {x["difficulty"]: x["count"] for x in progress_result["numFailedQuestions"]}
            untouched = {x["difficulty"]: x["count"] for x in progress_result["numUntouchedQuestions"]}
            beats = {x["difficulty"]: x["percentage"] for x in progress_result["userSessionBeatsPercentage"]}

            for diff in ["EASY", "MEDIUM", "HARD"]:
                result_table.append([
                    diff.capitalize(),
                    accepted.get(diff, 0),
                    failed.get(diff, 0),
                    untouched.get(diff, 0),
                    f"{beats.get(diff):.2f}" if beats.get(diff) is not None else "-"
                ])
            return tabulate(result_table, headers=["Difficulty", "Accepted", "Failed", "Untouched", "Beats (%)"], tablefmt="fancy_grid") 
       
        except Exception as e:
            raise e