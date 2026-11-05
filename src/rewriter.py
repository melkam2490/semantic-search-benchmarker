import re


def rewrite_query(query, conversation_context=""):
    """
    Rewrite a conversational question using previous context.
    """

    query = query.strip()
    conversation_context = conversation_context.strip()

    if not query:
        return ""

    if not conversation_context:
        return query

    replacements = {
        r"\bits\b": f"{conversation_context}'s",
        r"\bit\b": conversation_context,
        r"\bthat\b": f"the approach for {conversation_context}",
        r"\bthey\b": conversation_context,
        r"\bthem\b": conversation_context,
        r"\btheir\b": f"{conversation_context}'s",
    }

    rewritten = query

    for pattern, replacement in replacements.items():
        rewritten = re.sub(
            pattern,
            replacement,
            rewritten,
            flags=re.IGNORECASE
        )

    return rewritten