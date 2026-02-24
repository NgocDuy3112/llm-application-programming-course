from tavily import TavilyClient
from enum import Enum


class IncludeAnswerType(str, Enum):
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"



class SearchService:
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, include_answer: IncludeAnswerType = IncludeAnswerType.NONE) -> dict:
        """Perform a search query and return results."""
        try:
            results = self.client.search(query=query, include_answer=include_answer)
            return results
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")