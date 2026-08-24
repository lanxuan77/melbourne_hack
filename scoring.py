import re


# Keep accessibility mode names in ONE place
MODES = [
    "Simplify language",
    "Reduce cognitive load",
    "Improve visual accessibility",
    "Audio accessibility",
]

# Basic text helpers

def count_words(text):
    return len(text.split())


def count_sentences(text):
    sentences = re.split(r"[.!?]+", text)
    return len([sentence for sentence in sentences if sentence.strip()])


def average_sentence_length(text):
    words = count_words(text)
    sentences = count_sentences(text)

    if sentences == 0:
        return 0

    return words / sentences


def count_long_paragraphs(text, limit=100):
    paragraphs = text.split("\n\n")

    return sum(
        1
        for paragraph in paragraphs
        if len(paragraph.split()) > limit
    )


def clamp_score(score):
    """Keep accessibility scores between 0 and 100."""
    return max(0, min(score, 100))


# ---------------------------------------------------------
# Simplify language
# ---------------------------------------------------------

def score_language(text):
    score = 20

    avg_length = average_sentence_length(text)

    # Long sentences are harder to process
    if avg_length > 30:
        score -= 5
    elif avg_length > 20:
        score -= 2

    # Approximate difficult / technical vocabulary
    words = text.split()

    long_words = [
        word
        for word in words
        if len(re.sub(r"[^a-zA-Z]", "", word)) >= 12
    ]

    if len(long_words) > 10:
        score -= 5
    elif len(long_words) > 2:
        score -= 2

    return clamp_score(score * 5)


# ---------------------------------------------------------
# Reduce cognitive load
# ---------------------------------------------------------

def score_cognitive_load(text):
    score = 20

    words = count_words(text)
    long_paragraphs = count_long_paragraphs(text)

    # Too much content can increase cognitive load
    if words > 700:
        score -= 5
    elif words > 500:
        score -= 3

    # Long paragraphs are harder to process
    if long_paragraphs >= 3:
        score -= 5
    elif long_paragraphs >= 1:
        score -= 2

    # Headings improve structure
    headings = text.count("#")

    if headings == 0:
        score -= 3

    # Bullets help break information into chunks
    bullets = text.count("-") + text.count("•")

    if bullets == 0:
        score -= 3

    # Numbered steps help with instructions
    numbered_steps = len(
        re.findall(r"(?m)^\s*\d+[\.\)]\s+", text)
    )

    if numbered_steps == 0:
        score -= 2

    return clamp_score(score * 5)


# ---------------------------------------------------------
# Improve visual accessibility
# ---------------------------------------------------------

def score_visual(text):
    score = 20

    # Headings
    headings = text.count("#")

    if headings == 0:
        score -= 5
    elif headings < 3:
        score -= 2

    # Bullet points
    bullets = text.count("-") + text.count("•")

    if bullets == 0:
        score -= 3
    elif bullets < 3:
        score -= 1

    # Numbered steps
    numbered_steps = len(
        re.findall(r"(?m)^\s*\d+[\.\)]\s+", text)
    )

    if numbered_steps == 0:
        score -= 2

    # Image / diagram descriptions
    description_patterns = [
        "image description",
        "image:",
        "diagram:",
        "figure:",
        "alt text",
        "description:",
    ]

    description_count = sum(
        text.lower().count(pattern)
        for pattern in description_patterns
    )

    if description_count == 0:
        score -= 3

    # Avoid relying only on colour
    colour_words = [
        "red",
        "green",
        "blue",
        "yellow",
        "orange",
    ]

    colour_count = sum(
        text.lower().count(word)
        for word in colour_words
    )

    if (
        colour_count > 0
        and "not rely on colour" not in text.lower()
    ):
        score -= 2

    return clamp_score(score * 5)


# ---------------------------------------------------------
# Audio accessibility
# ---------------------------------------------------------

def score_audio(text):
    score = 20

    avg_length = average_sentence_length(text)

    # Shorter sentences are easier to follow when heard aloud
    if avg_length > 30:
        score -= 5
    elif avg_length > 20:
        score -= 3

    # Transitions make spoken content easier to follow
    transitions = [
        "first",
        "firstly",
        "next",
        "then",
        "finally",
        "in other words",
        "for example",
        "to summarise",
        "in summary",
    ]

    transition_count = sum(
        text.lower().count(word)
        for word in transitions
    )

    if transition_count == 0:
        score -= 3

    # Explanatory phrasing supports audio comprehension
    explanation_patterns = [
        "means",
        "refers to",
        "in other words",
        "simply put",
        "in simple terms",
    ]

    explanation_count = sum(
        text.lower().count(pattern)
        for pattern in explanation_patterns
    )

    if explanation_count == 0:
        score -= 2

    return clamp_score(score * 5)


# ---------------------------------------------------------
# Overall scoring
# ---------------------------------------------------------

def calculate_score(text, mode):
    if mode == "Simplify language":
        score = score_language(text)

    elif mode == "Reduce cognitive load":
        score = score_cognitive_load(text)

    elif mode == "Improve visual accessibility":
        score = score_visual(text)

    elif mode == "Audio accessibility":
        score = score_audio(text)

    else:
        raise ValueError(f"Unknown accessibility mode: {mode}")

    return {
        "score": score,
        "mode": mode,
    }


def compare_scores(original, adapted, mode):
    before = calculate_score(original, mode)
    after = calculate_score(adapted, mode)

    improvement = after["score"] - before["score"]

    return {
        "mode": mode,
        "before": before["score"],
        "after": after["score"],
        "improvement": improvement,
    }


def compare_multiple_scores(original, adapted, modes):
    results = []

    for mode in modes:
        result = compare_scores(
            original,
            adapted,
            mode,
        )

        results.append(result)

    if not results:
        return {
            "before": 0,
            "after": 0,
            "improvement": 0,
            "details": [],
        }

    before_average = sum(
        result["before"]
        for result in results
    ) / len(results)

    after_average = sum(
        result["after"]
        for result in results
    ) / len(results)

    improvement = after_average - before_average

    return {
        "before": round(before_average),
        "after": round(after_average),
        "improvement": round(improvement),
        "details": results,
    }
