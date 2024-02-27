from datetime import datetime
import json
import sys, os
sys.path.append(rf'{os.path.abspath(".")}')
from Strategies.strategy_abc import Strategy


def record_analytics(word: str, strategies: dict[str: Strategy], analytics: dict, exhibition=False):
    new_strategies = {
        strategy_name: {
            "solved": strategy.correctly_guessed,
            "exhibition": exhibition,
            "attempts": strategy.attempts,
            "analytics": strategy.analytics
        }
        for strategy_name, strategy in strategies.items()
    }

    now = datetime.now().strftime("%Y-%m-%d")
    word_analytics = analytics.get(word, {})
    now_analytics = word_analytics.get(now, {})

    if now_analytics.get("strategies"):
        now_analytics["strategies"].update(new_strategies)
    else:
        now_analytics.update({"strategies": new_strategies})

    if now in word_analytics.keys():
        word_analytics[now].update(now_analytics)
    else:
        word_analytics.update({now: now_analytics})

    if word in analytics.keys():
        analytics[word].update(word_analytics)
    else:
        analytics.update({word: word_analytics})

    analytics = analyze_results(word, analytics, now)

    json.dump(analytics, open(fr"{os.path.dirname(__file__)}\..\assets\analytics.json", "w"))

    return analytics


def analyze_results(word: str, analytics: dict, word_date: str):
    word_date_analytics = analytics.get(word, {}).get(word_date, {})
    if not word_date_analytics:
        raise KeyError(f"Unable to locate {word}>{word_date} in analytics!")

    best_attempts = ""
    best_attempts_score = None
    best_reduced_words = ""
    best_reduced_words_score = None
    best_time_to_generate_word_ns = ""
    best_time_to_generate_word_ns_score = None

    strategies = word_date_analytics.get("strategies")
    ranking = []
    for strategy_name, strategy in strategies.items():
        attempts = strategy.get("attempts", 1)
        attempts = 1 if attempts == 0 else attempts
        total_reduced_words = 0
        total_time_to_generate_word_ns = 0
        for analytic in strategy.get("analytics", []):
            total_reduced_words += analytic.get("reduced_words_exact", 0)
            total_time_to_generate_word_ns += analytic.get("time_to_generate_word_ns", 0)

        average_reduced_words = total_reduced_words / attempts
        average_time_to_generate_word_ns = total_time_to_generate_word_ns / attempts

        analytics_copy = strategy.get("analytics", [])
        if analytics_copy: strategy.pop("analytics")
        strategy.update({
            "average_reduced_words_exact": average_reduced_words,
            "average_reduced_words": f"{int(average_reduced_words * 100)}%",
            "average_time_to_generate_word_ns": int(average_time_to_generate_word_ns),
            "analytics": analytics_copy
        })

        if best_attempts_score is None or attempts < best_attempts_score:
            best_attempts = strategy_name
            best_attempts_score = attempts

        if best_reduced_words_score is None or average_reduced_words > best_reduced_words_score:
            best_reduced_words = strategy_name
            best_reduced_words_score = average_reduced_words

        if best_time_to_generate_word_ns_score is None or average_time_to_generate_word_ns < best_time_to_generate_word_ns_score:
            best_time_to_generate_word_ns = strategy_name
            best_time_to_generate_word_ns_score = average_time_to_generate_word_ns

        ranking.append(strategy_name)

    for i in range(len(ranking)):
        swapped = False

        for j in range(0, len(ranking) - i - 1):
            bubble = False
            rank_strategy_lhs = strategies.get(ranking[j])
            rank_strategy_rhs = strategies.get(ranking[j + 1])
            attempts_lhs = rank_strategy_lhs.get("attempts")
            attempts_rhs = rank_strategy_rhs.get("attempts")
            average_reduced_words_lhs = rank_strategy_lhs.get("average_reduced_words_exact")
            average_reduced_words_rhs = rank_strategy_rhs.get("average_reduced_words_exact")
            average_time_to_generate_word_ns_lhs = rank_strategy_lhs.get("average_time_to_generate_word_ns")
            average_time_to_generate_word_ns_rhs = rank_strategy_rhs.get("average_time_to_generate_word_ns")

            if attempts_lhs > attempts_rhs:  # more attempts, higher up on the list
                bubble = True
            elif attempts_lhs == attempts_rhs:
                if average_reduced_words_lhs < average_reduced_words_rhs:
                    bubble = True
                elif average_reduced_words_lhs == average_reduced_words_rhs:
                    if average_time_to_generate_word_ns_lhs > average_time_to_generate_word_ns_rhs:
                        bubble = True

            if bubble:
                ranking[j], ranking[j + 1] = ranking[j + 1], ranking[j]
                swapped = True

        if not swapped: break

    word_date_analytics.pop("strategies")
    word_date_analytics.update({
        "best_attempt": best_attempts,
        "best_average_reduced_words": best_reduced_words,
        "best_average_time_to_generate_word_ns": best_time_to_generate_word_ns,
        "ranking": ranking,
        "strategies": strategies
    })

    _n = "\n"
    _t = "\t"

    print("\n***** Analytics Results *****")
    print(
        f"""Strategy with the shortest number of attempts: {best_attempts}
Completed with {best_attempts_score} attempts.

Strategy with greatest number of average reduced words per round: {best_reduced_words}
Reduced {best_reduced_words_score} words on average per round.

Strategy with shortest average time to generate a word per round: {best_time_to_generate_word_ns}
Took {best_time_to_generate_word_ns_score} nanoseconds on average per round.


***** Strategy Ranking *****
{f"{_n}".join([f"{_i + 1}: {ranking[_i]}" for _i in range(len(ranking))])}


***** Individual Strategy Game Completion Details *****
{
f"{_n}{_n}".join([
    f"{strat}:"
    f"{_n}{_t}{'Solved solution!' if strats.get('solved') else 'Unable to solve solution.'}"
    f"{_n}{_t}Attempts: {strats.get('attempts')}"
    f"{_n}{_t}Average reduced words: {strats.get('average_reduced_words')}"
    f"{_n}{_t}Average time to generate word in nanoseconds: {strats.get('average_time_to_generate_word_ns')}"
    for strat, strats in strategies.items()
])
}
"""
    )

    return analytics
