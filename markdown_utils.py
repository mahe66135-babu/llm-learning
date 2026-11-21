
import re


def validate_markdown(content: str) -> bool:
    """Check whether an AI response contains valid basic Markdown structure."""

    if not isinstance(content, str):
        return False

    if not content.strip():
        return False

    # Detect opening and closing fenced code blocks,
    # allowing indentation before the fence.
    code_fence_count = len(
        re.findall(r"^[ \t]*```", content, flags=re.MULTILINE)
    )

    if code_fence_count % 2 != 0:
        return False

    return True
