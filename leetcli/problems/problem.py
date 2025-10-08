import os
import json
import requests
from tabulate import tabulate
from bs4 import BeautifulSoup

from leetcli.utils.query import (
    _req_problem_query,
    _req_problem_detail_query,
    _req_problem_daily_query,
    _req_problem_solution_detail_query
)
from leetcli.utils.variable import (
    _req_problem_variable,
    _req_one_problem_variable,
    _req_problem_detail_variable,
    _req_problem_submit_variable,
    _req_problem_solution_detail_variable
)
from leetcli.utils.req import (
    _req_header, 
    _req_cookies,
    _req_solution_header
)
from leetcli.utils.file import (
    _create_code_file,
    _create_markdown_file,
    _get_code_str
)
from leetcli.utils.language import (
    _detect_language
)
from leetcli.problems.status_code import STATUS_CODE_MAP

LEETCODE_URL = "https://leetcode.com/graphql"

class ProblemManager():
    def __init__(self):
        pass

    def _get_problemlist(
        self, 
        csrftoken, 
        session, 
        mode,
        difficulty,
        start
    ):
        try:
            table_data = []
            headers = _req_header(csrftoken)
            cookies = _req_cookies(
                session, 
                csrftoken,
            )
            query = _req_problem_query()
            variables = _req_problem_variable(
                mode,
                difficulty,
                start
            )
            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": query, "variables": variables})
            )
            
            response = response.json()
            questions = response['data']['problemsetQuestionList']['questions']

            for question in questions:
                ac_rate = float(question['acRate'])
                ac_rate_str = f"{ac_rate:.2f}%"
                status_map = {"ac": "✅", "notac": "⚠️", None: "❌"}
                table_data.append([
                    question['questionFrontendId'],
                    question['title'],
                    question['difficulty'],
                    ac_rate_str,
                    question['isPaidOnly'],
                    status_map[question['status']]
                ])
            return tabulate(
                table_data,
                headers=["ID", "Title", "Difficulty", "Acceptance", "isPaidOnly", "Status"],
                tablefmt="fancy_grid"
            )
        
        except Exception as e:
            raise e

    def _get_daily_problem(
        self,
        csrftoken, 
        session,
    ):
        try:
            table_data = []
            headers = _req_header(csrftoken)
            cookies = _req_cookies(
                    session, 
                    csrftoken,
            )
            query = _req_problem_daily_query()

            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": query})
            )
            response = response.json()
            question = response['data']['activeDailyCodingChallengeQuestion']['question']
            
            ac_rate = json.loads(question["stats"])["acRate"]
            status_map = {"ac": "✅", "notac": "⚠️", None: "❌"}
            table_data.append([
                question['questionFrontendId'],
                question['title'],
                question['difficulty'],
                ac_rate,
                question['isPaidOnly'],
                status_map[question['status']]
            ])
            return tabulate(
                table_data,
                headers=["ID", "Title", "Difficulty", "Acceptance", "isPaidOnly", "Status"],
                tablefmt="fancy_grid"
            )
        except Exception as e:
            raise e

    def _download_problem(
        self, 
        csrftoken, 
        session,
        problem_id,
        language
    ):
        try:
            headers = _req_header(csrftoken)
            cookies = _req_cookies(
                    session, 
                    csrftoken,
            )
            query = _req_problem_query()
            variables = _req_one_problem_variable(problem_id)

            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": query, "variables": variables})
            )
            response = response.json()
            questions = response['data']['problemsetQuestionList']['questions']
            
            titleSlug = questions[0]['titleSlug']

            detail_query = _req_problem_detail_query()
            variables = _req_problem_detail_variable(titleSlug)

            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": detail_query, "variables": variables})
            )
            data = response.json()['data']['question']
            ac_rate = json.loads(data["stats"])["acRate"]
            soup = BeautifulSoup(data['content'], 'html.parser')
            content_text = soup.get_text()
            
            _create_markdown_file(
                data, 
                content_text, 
                ac_rate
            )
            _create_code_file(
                data, 
                language
            )

        except TypeError as e:
            raise TypeError(
                f"This question is only for paid user"
            )

        except Exception as e:
            raise e


    def _download_problem_daily(
        self,
        csrftoken,
        session,
        language
    ):
        try:
            headers = _req_header(csrftoken)
            cookies = _req_cookies(
                    session, 
                    csrftoken,
            )
            query = _req_problem_daily_query()

            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": query})
            )
            response = response.json()
            response = response
            question = response['data']['activeDailyCodingChallengeQuestion']['question']
            problem_id = int(question['questionFrontendId'])

            self._download_problem(
                csrftoken, 
                session, 
                problem_id, 
                language
            )

        except Exception as e:
            raise e

    def _submit_problem(
        self,
        csrftoken,
        session,
        problem_id,
        filename,
    ):
        try:
            headers = _req_header(csrftoken)
            cookies = _req_cookies(
                    session, 
                    csrftoken,
            )

            basename = os.path.basename(filename)
            _, ext = os.path.splitext(basename)
            language = _detect_language(ext)
        
            query = _req_problem_query()
            variables = _req_one_problem_variable(problem_id)

            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": query, "variables": variables})
            )
            
            response = response.json()
            question = response['data']['problemsetQuestionList']['questions']
            
            titleSlug = question[0]['titleSlug']
            problem_id_internal = question[0]['questionId']

            code = _get_code_str(filename)
            solution_headers = _req_solution_header(
                csrftoken,
                titleSlug
            )

            data = _req_problem_submit_variable(
                language,
                code,
                problem_id_internal
            )
            url = f"https://leetcode.com/problems/{titleSlug}/submit/"
            response = requests.post(
                url, 
                headers=solution_headers, 
                cookies=cookies, 
                json=data
            )
            submission_id = json.loads(response.content)['submission_id']
            return int(submission_id)

        except Exception as e:
            raise e
        
    def _check_submit_problem(
        self,
        csrftoken,
        session,
        submission_id
    ):
        try:
            result_table = []
            headers = _req_header(csrftoken)
            cookies = _req_cookies(
                    session, 
                    csrftoken,
            )
            query = _req_problem_solution_detail_query()
            variables = _req_problem_solution_detail_variable(submission_id)

            response = requests.post(
                LEETCODE_URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps({"query": query, "variables": variables})
            )
            
            result = json.loads(response.content)
            data = result["data"]["submissionDetails"]
            status = STATUS_CODE_MAP.get(data["statusCode"], f"Unknown ({data['statusCode']})")
            result_table.append([
                data["statusCode"],
                status,
                data["runtime"],
                data["memory"],
                f"{data['totalCorrect']}/{data['totalTestcases']}",
                data["runtimeError"][:60] + "..." if data["runtimeError"] else ""
            ])
            table_headers = ["Status Code", "Result", "Runtime (ms)", "Memory (KB)", "Passed", "Runtime Error"]
            return tabulate(result_table, headers=table_headers, tablefmt="fancy_grid")

        except Exception as e:
            raise e
