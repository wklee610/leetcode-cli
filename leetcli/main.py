import time
import click
from leetcli.auth.user import *
from leetcli.problems.problem import *
from leetcli.utils.language import LEETCODE_LANGUAGES

LEETCODE_URL = "https://leetcode.com/graphql"
LEETCODE_LOGIN_PAGE = "https://leetcode.com/accounts/login/"

class LeetCli:
    """
    LeetCli - LeetCode Helper CLI

    Provides commands to:
    - Login / logout to LeetCode
    - Check user status and problem-solving progress
    - Download problems
    - Submit solutions
    - Set default language for submissions
    """
    def __init__(self):
        """
        Initialize LeetCli instance.

        - Loads user info from local session if available
        - Retrieves csrf token, session, and default language
        - Initializes ProblemManager
        - Adds all CLI commands to `self.cli`
        """
        self.cli = click.Group(help="leetcli - LeetCode Helper CLI")
        self.user_manager = UserInfoManager()
        try:
            self.csrftoken = self.user_manager._get_csrftoken()
            self.session = self.user_manager._get_session()
            self.language = self.user_manager._get_lang()

        except ConnectionError as e:
            self.userinfo = ConnectionError

        except Exception:
            self.userinfo = Exception
            self.csrftoken = None
            self.session = None
        self.problem_manager = ProblemManager()
        self._add_commands()

    def _add_commands(self):
        self.cli.add_command(self.login)
        self.cli.add_command(self.status)
        self.cli.add_command(self.logout)
        self.cli.add_command(self.problem)
        self.cli.add_command(self.set)
        self.cli.add_command(self.get)
        self.cli.add_command(self.submit)

    @click.command()
    @click.option(
        "--default-language",
        prompt="Set default language",
        help="Set default programming language.",
    )
    @click.pass_obj
    def login(obj, default_language):
        """
        Login to LeetCode and save session info locally.

        Steps:
        - Extract cookies from browser session
        - Save cookies and default language locally
        - Verify login and display current user

        Options:
        --default-language: Default language to use for submissions

        Notes:
        - On macOS Safari, policies may restrict browser access.
        - If login fails, you may need to log in manually via the browser.
        """
        try:
            cookies = obj.user_manager._create_userinfo()
            obj.user_manager._save_userinfo(
                cookies, 
                default_language, 
                LEETCODE_LANGUAGES
            )

            click.secho("Checking current login status...", fg="yellow")
            
            obj.userinfo = obj.user_manager._get_userinfo(LEETCODE_URL)
            if isinstance(obj.userinfo, (list, tuple)) and obj.userinfo[0]:
                click.secho(f"""Logged in successfully!\nCurrent user: {obj.userinfo[1]}""", fg="green")
            else:
                click.secho(f"Please log in using main browser: {LEETCODE_LOGIN_PAGE}", fg="red")
                click.secho("(On Safari, macOS policies restrict access to browser information.)", fg="red")

        except TypeError as e:
            click.secho(f"Please log in properly.", fg="red")
            click.secho(f"If you haven't logged in before,", fg="red")
            click.secho(f"Please log in using main browser: {LEETCODE_LOGIN_PAGE}", fg="red")
            click.secho("(On Safari, macOS policies restrict access to browser information.)", fg="red")

        except ConnectionError as e:
            click.secho(f"""Check internet connection. """, fg="red")

        except ValueError as e:
            click.secho(str(e), fg="red")

        except Exception as e:
            if isinstance(cookies, str):
                click.secho(cookies, fg="red")
            else:
                click.secho("An unknown error occurred. Please report this issue on GitHub.", fg="red")

    @click.command()
    @click.pass_obj
    def status(obj):
        """
        Check current login status and problem-solving progress.

        Displays:
        - Whether user is logged in
        - Current username
        - Progress summary (solved / unsolved / attempted problems)
        """
        try:
            obj.userinfo = obj.user_manager._get_userinfo(LEETCODE_URL)
            if isinstance(obj.userinfo, (list, tuple)) and obj.userinfo[0]:
                user_progress = obj.user_manager._get_user_progress(
                    obj.csrftoken,
                    obj.session,
                    obj.userinfo
                )
                click.secho(f"""Login: {obj.userinfo[0]}\nCurrent user: {obj.userinfo[1]}""", fg="green")
                click.secho(user_progress, fg="bright_white")

            else:
                click.secho(f"""Login Failed\nUse "leetcli login" """, fg="red")
        except ConnectionError as e:
            click.secho(f"""Check internet connection. """, fg="red")

        except FileNotFoundError as e:
            click.secho(f"""Login Failed\nUse "leetcli login" """, fg="red")

        except Exception as e:
            click.secho(f"An unknown error occurred. Please report this issue on GitHub. {e}", fg="red")

    @click.command()
    @click.pass_obj
    def logout(obj):
        """
        Logout from LeetCode.

        Deletes local session info stored in:
        ~/.leetcode-cli/session.json
        """
        try:
            is_deleted = obj.user_manager._delete_userinfo()
            if is_deleted:
                click.secho("Logged out successfully!", fg="green")
            else:
                click.secho("No active login session found.", fg="red")

        except ConnectionError as e:
            click.secho("""Failed to logout, try to delete manually in ~/.leetcode-cli/session.json""", fg="red")
        
    @click.command()
    @click.argument("daily", required=False)
    @click.option(
        "-a", "--all", 
        "mode",
        flag_value="all",
        default=True,
        help="Show all problems (default)"
    )
    @click.option(
        "-s", "--solved", 
        "mode",
        flag_value="solved",
        help="Show only solved problems"
    )
    @click.option(
        "-u", "--unsolved", 
        "mode",
        flag_value="unsolved",
        help="Show only unsolved problems"
    )
    @click.option(
        "-t", "--tried", 
        "mode",
        flag_value="tried",
        help="Show only tried problems"
    )
    @click.option(
        "--diff",
        type=click.Choice(["easy", "medium", "hard"], case_sensitive=False),
        default=None,
        help="Filter by difficulty (easy, medium, hard)"
    )
    @click.option(
        "--start",
        default=0,
        type=int,
        show_default=True,
        help="Start index (e.g., --start=50)"
    )
    @click.pass_obj
    def problem(obj, daily, mode, diff, start):
        """
        Search and display problems.

        Arguments:
        daily: "daily" to fetch daily problem, otherwise ignore
        mode: Filter by solved / unsolved / tried / all
        diff: Filter by difficulty (easy, medium, hard)
        start: Start index for pagination

        Notes:
        - Default mode shows all problems.
        - Can combine with difficulty filter.
        """
        try:
            if daily == 'daily':
                result = obj.problem_manager._get_daily_problem(
                    obj.csrftoken,
                    obj.session,

                )

            elif daily == None:
                result = obj.problem_manager._get_problemlist(
                    obj.csrftoken, 
                    obj.session, 
                    mode, 
                    diff,
                    start,
                )
            else:
                click.secho(f"""Use "leetcli problem daily" or "leetcli problem [-option] [--start] """, fg="red")
            
            click.secho(result, fg="bright_white") 

        except requests.exceptions.ConnectionError as e:
            click.secho(f"""Check internet connection. """, fg="red")

        except FileNotFoundError as e:
            click.secho(f"""Login Failed\nUse "leetcli login" """, fg="red")

        except Exception as e:
            click.secho(f"An unknown error occurred. Please report this issue on GitHub. ({e})", fg="red")

    @click.command()
    @click.argument("language", required=True)
    @click.pass_obj
    def set(obj, language):
        """
        Set default language for submissions.

        Arguments:
        language: Name or abbreviation of the programming language.

        Notes:
        - Supported languages are defined in LEETCODE_LANGUAGES.
        """
        try:
            result = obj.user_manager._set_lang(
                language,
                LEETCODE_LANGUAGES
            )
            click.secho(f"Default language changed to: {result}", fg="blue")

        except FileNotFoundError:
            click.secho("User info file not found. Please log in first.", fg="red")

        except ValueError as e:
            click.secho(str(e), fg="red")

        except Exception as e:
            click.secho(f"An unknown error occurred. Please report this issue on GitHub. {e}", fg="red")

    @click.command()
    @click.argument("problem_id", required=True)
    @click.argument("language", required=False)
    @click.pass_obj
    def get(obj, problem_id, language):
        """
        Download a problem from LeetCode.

        Arguments:
        problem_id: Problem frontend ID or "daily"
        language: Optional, use default language if not provided

        Notes:
        - Downloads problem template in the specified language.
        - Supports both relative and absolute file paths.
        """
        try:
            if language == None:
                language = obj.language
            else:
                language = language

            if problem_id == 'daily':
                obj.problem_manager._download_problem_daily(
                    obj.csrftoken,
                    obj.session,
                    language
                )
            
            else:
                problem_id = int(problem_id)
                obj.problem_manager._download_problem(
                    obj.csrftoken, 
                    obj.session,
                    problem_id,
                    language
                )
            return click.secho(f"""Download Succeed!""", fg="green")
            
        except requests.exceptions.ConnectionError as e:
            click.secho(f"""Check internet connection. """, fg="red")

        except TypeError as e:
            click.secho(str(e), fg="red")

        except FileNotFoundError as e:
            click.secho(f"""Login Failed\nUse "leetcli login" """, fg="red")

        except ValueError as e:
            click.secho(f"""Please enter either "leetcli get daily" or a "leetcli get [problem_id]".""", fg="red")

        except AttributeError as e:
            click.secho(f"""Failed to get language, try "leetcli set [language]" """, fg="red")

        except Exception as e:
            click.secho(f"An unknown error occurred. Please report this issue on GitHub. {e}", fg="red")


    @click.command()
    @click.argument("problem_id", type=int, required=True)
    @click.argument(
        "filename", 
        type=click.Path(exists=True),
        required=True
    )
    @click.pass_obj
    def submit(obj, problem_id, filename):
        """
        Submit a solution file to LeetCode.

        Arguments:
        problem_id: LeetCode problem frontend ID
        filename: Path to solution file (relative or absolute)

        Notes:
        - File extension or language name is used to detect submission language.
        - Waits for 10 seconds before checking submission result.
        """
        try:
            submission_id = obj.problem_manager._submit_problem(
                obj.csrftoken,
                obj.session,
                problem_id,
                filename,
            )
            time.sleep(10)
            result = obj.problem_manager._check_submit_problem(
                obj.csrftoken,
                obj.session,
                submission_id
            )
            return click.secho(result, fg="bright_white")

        except requests.exceptions.ConnectionError as e:
            click.secho(f"""Check internet connection. """, fg="red")

        except ValueError as e:
            click.secho(str(e), fg="red")

        except FileNotFoundError as e:
            click.secho(f"""Login Failed\nUse "leetcli login" """, fg="red")

        except Exception as e:
            click.secho(f"An unknown error occurred. Please report this issue on GitHub. {e}", fg="red")


    def run(self):
        """EntryPoint"""
        self.cli(obj=self)


def main():
    app = LeetCli()
    app.run()

