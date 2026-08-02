"""
FacultyIQ Coding Intelligence Agent — Question Pydantic Schemas.
"""

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class BloomLevel(str, Enum):
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class Category(str, Enum):
    ARRAYS = "arrays"
    STRINGS = "strings"
    LINKED_LIST = "linked_list"
    STACK = "stack"
    QUEUE = "queue"
    TREES = "trees"
    BST = "bst"
    HEAP = "heap"
    HASHMAP = "hashmap"
    GRAPHS = "graphs"
    DFS = "dfs"
    BFS = "bfs"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    GREEDY = "greedy"
    TRIE = "trie"
    SEGMENT_TREE = "segment_tree"
    BACKTRACKING = "backtracking"
    BIT_MANIPULATION = "bit_manipulation"
    SQL = "sql"
    DEBUGGING = "debugging"
    SYSTEM_DESIGN = "system_design"


class SupportedLanguage(str, Enum):
    PYTHON = "python"
    C = "c"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    CSHARP = "csharp"


class TestCaseDTO(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    is_stress: bool = False
    is_edge_case: bool = False
    description: str = ""
    time_limit_ms: int = 5000


class QuestionDTO(BaseModel):
    id: str
    title: str
    description: str
    category: str
    difficulty: str
    bloom_level: str = "Apply"
    tags: List[str] = Field(default_factory=list)
    constraints: str = ""
    expected_time_complexity: str = ""
    expected_space_complexity: str = ""
    starter_code: Dict[str, str] = Field(default_factory=dict)
    hints: List[str] = Field(default_factory=list)
    public_test_cases: List[TestCaseDTO] = Field(default_factory=list)
    is_debugging: bool = False
    buggy_code: Dict[str, str] = Field(default_factory=dict)
    bug_description: str = ""


class QuestionFilter(BaseModel):
    category: Optional[str] = None
    difficulty: Optional[str] = None
    bloom_level: Optional[str] = None
    language: Optional[str] = None
    exclude_ids: List[str] = Field(default_factory=list)
    is_debugging: Optional[bool] = None


class QuestionListResponse(BaseModel):
    questions: List[QuestionDTO]
    total: int
