from typing import TypedDict, List

class ConversationState(TypedDict):
    phase: int
    history: List[str]
    last_response: str