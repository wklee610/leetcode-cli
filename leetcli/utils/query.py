def _req_problem_query() -> str:
    return """
        query getProblems($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                total: totalNum
                questions: data {
                    questionId
                    acRate
                    difficulty
                    freqBar
                    questionFrontendId
                    isFavor
                    isPaidOnly
                    status
                    title
                    titleSlug
                    topicTags {
                        name
                        id
                        slug
                    }
                    hasSolution
                    hasVideoSolution
                }
            }
        }
        """

def _req_problem_detail_query() -> str:
    return """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionFrontendId
                title
                content
                difficulty
                stats
                codeSnippets {
                    lang
                    code
                }
            }
        }
        """

def _req_problem_daily_query() -> str:
    return """
        query getDailyProblem {
            activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    questionId
                    questionFrontendId
                    boundTopicId
                    title
                    titleSlug
                    content
                    translatedTitle
                    translatedContent
                    isPaidOnly
                    difficulty
                    likes
                    dislikes
                    isLiked
                    similarQuestions
                    exampleTestcases
                    contributors {
                        username
                        profileUrl
                        avatarUrl
                    }
                    topicTags {
                        name
                        slug
                        translatedName
                    }
                    companyTagStats
                    codeSnippets {
                        lang
                        langSlug
                        code
                    }
                    stats
                    hints
                    solution {
                        id
                        canSeeDetail
                        paidOnly
                        hasVideoSolution
                        paidOnlyVideo
                    }
                    status
                    sampleTestCase
                    metaData
                    judgerAvailable
                    judgeType
                    mysqlSchemas
                    enableRunCode
                    enableTestMode
                    enableDebugger
                    envInfo
                    libraryUrl
                    adminUrl
                    challengeQuestion {
                        id
                        date
                        incompleteChallengeCount
                        streakCount
                        type
                    }
                    note
                }
            }
        }
    """

def _req_problem_solution_detail_query() -> str:
    return """
        query submissionDetails($submissionId: Int!) {
            submissionDetails(submissionId: $submissionId) {
                statusCode
                runtime
                memory
                totalCorrect
                totalTestcases
                lastTestcase
                compileError
                runtimeError
            }
        }
    """

def _req_user_progress_v2_query() -> str:
    return """
        query userProfileUserQuestionProgressV2($userSlug: String!) {
            userProfileUserQuestionProgressV2(userSlug: $userSlug) {
                numAcceptedQuestions {
                    difficulty
                    count
                }
                numFailedQuestions {
                    difficulty
                    count
                }
                numUntouchedQuestions {
                    difficulty
                    count
                }
                userSessionBeatsPercentage {
                    difficulty
                    percentage
                }
            }
        }
    """