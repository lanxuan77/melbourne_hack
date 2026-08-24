import re

MODES = [
    "Simplify Language",
    "Reduce Cognitive Load",
    "Improve Visual Accessibility",
    "Audio accessibility"
]

def count_words(text):
    return len(text.split())

def count_sentences(text):
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])

def average_sentence_length(text):
    words = count_words(text)
    sentences = count_sentences(text)

    if sentences == 0:
        return 0

    return words / sentences

def count_long_paragraphs(text, limit=100):
    paragraphs = text.split("\n\n")

    count = 0

    for paragraph in paragraphs:
        if len(paragraph.split()) > limit:
            count += 1

    return count

#simplify language
def score_language(text):

    score = 20

    avg_length = average_sentence_length(text)

    #long sentences are harder to read
    if avg_length > 30:
        score -= 5
    elif avg_length > 20:
        score -= 2

    #look for technical terms / long words
    words = text.split()

    long_words = [word for word in words if len(re.sub(r'[^a-zA-Z]', '', word)) >= 12]

    if len(long_words) > 10:
        score -= 5
    elif len(long_words) > 2:
        score -= 2

    score = score * 5

    return max(score, 0)

#cognitive load
def score_cognitive_load(text):

    score = 20

    words = count_words(text)
    long_paragraphs = count_long_paragraphs(text)

    #too much content
    if words > 700:
        score -= 5
    elif words > 500:
        score -= 3

    #long paragraphs increase cognitive load
    if long_paragraphs >= 3:
        score -= 5
    elif long_paragraphs >= 1:
        score -= 2

    #headings help organise information
    headings = text.count("#")

    if headings == 0:
        score -= 3

    bullets = text.count("-") + text.count("•")

    if bullets == 0:
        score -= 3

    # numbered steps help with complex instructions
    numbered_steps = len(
        re.findall(r'(?m)^\s*\d+[\.\)]\s+', text)
    )

    if numbered_steps == 0:
        score -= 2

    score = score * 5

    return max(score, 0)


#visual organisation
def score_visual(text):

    score = 20

    #headings
    headings = text.count("#")

    if headings >= 3:
        score += 0
    elif headings == 0:
        score -= 5
    else:
        score -= 2

    #bullet points
    bullets = text.count("-") + text.count("•")

    if bullets == 0:
        score -= 3
    elif bullets < 3:
        score -= 1

    numbered_steps = len(
        re.findall(r'(?m)^\s*\d+[\.\)]\s+', text)
    )

    if numbered_steps == 0:
        score -= 2

    #image/diagram descriptions
    description_patterns = [
        "image description",
        "image:",
        "diagram:",
        "figure:",
        "alt text",
        "description:"
    ]

    description_count = sum(
        text.lower().count(pattern)
        for pattern in description_patterns
    )

    if description_count == 0:
        score -= 3

    # avoid relying on colour alone
    colour_words = [
        "red",
        "green",
        "blue",
        "yellow",
        "orange"
    ]

    colour_count = sum(text.lower().count(word) for word in colour_words)

    if colour_count > 0 and "not rely on colour" not in text.lower():
        score -= 2

    #tables
    if "|" not in text:
        score -= 3

    score = score * 5

    return max(score, 0)

#audio friendly
def score_audio(text):

    score = 20

    avg_length = average_sentence_length(text)

    if avg_length > 30:
        score -= 5
    elif avg_length > 20:
        score -= 3

    #conversational transitions
    transitions = [
        "first",
        "firstly",
        "next",
        "then",
        "finally",
        "in other words",
        "for example",
        "to summarise",
        "in summary"
    ]

    transition_count = sum(text.lower().count(word) for word in transitions)

    if transition_count == 0:
        score -= 3

    explanation_patterns = [
        "means",
        "refers to",
        "in other words",
        "simply put",
        "in simple terms"
    ]

    explanation_count = sum(
        text.lower().count(pattern)
        for pattern in explanation_patterns
    )

    score = score * 5

    return max(score, 0)

#overall scoring
def calculate_score(text, mode):

    if mode == "Simplify Language":
        score = score_language(text)

    elif mode == "Reduce Cognitive Load":
        score = score_cognitive_load(text)

    elif mode == "Improve Visual Accessibility":
        score = score_visual(text)

    elif mode == "Add Audio-Friendly Alternatives":
        score = score_audio(text)

    else:
        raise ValueError("Unknown accessibility mode")

    return {
        "score": score,
        "mode": mode
    }

#compare before and after
def compare_scores(original, adapted, mode):

    before = calculate_score(original, mode)
    after = calculate_score(adapted, mode)

    improvement = after["score"] - before["score"]

    return {
        "before": before["score"],
        "after": after["score"],
        "improvement": improvement
    }

def compare_multiple_scores(original, adapted, modes):

    results = []

    for mode in modes:

        result = compare_scores(
            original,
            adapted,
            mode
        )

        results.append(result)

    if not results:
        return {
            "before": 0,
            "after": 0,
            "improvement": 0,
            "details": []
        }

    before_average = sum(
        result["before"] for result in results
    ) / len(results)

    after_average = sum(
        result["after"] for result in results
    ) / len(results)

    improvement = after_average - before_average

    return {
        "before": round(before_average),
        "after": round(after_average),
        "improvement": round(improvement),
        "details": results
    }

#testtest
'''
if __name__ == "__main__":

    original = """
    Photosynthesis is a complex biochemical process through
    which photoautotrophic organisms convert radiant energy
    into chemical energy.

    This process involves multiple interconnected biochemical
    pathways and cellular mechanisms.
    """

    adapted = """
    ## What is photosynthesis?

    Photosynthesis is how plants make food using light.

    ### Key idea

    - Plants use light energy.
    - Plants use water.
    - Plants use carbon dioxide.

    In simple terms, plants turn these ingredients into food.
    """

    result = compare_scores(
        original,
        adapted,
        "Simplify Language"
    )

    print(result)
'''
