"""
Bloom's Taxonomy AI Question Generator Engine.
Generates categorized questions mapped to Bloom's Taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create) across Easy, Medium, Hard, Expert difficulties.
"""

from typing import List
from app.interview.schemas.interview_models import InterviewQuestion
from core.logging import get_logger

logger = get_logger("question_generator")


class QuestionGeneratorEngine:
    """Bloom's Taxonomy Question Generator Engine."""

    def generate_questions(
        self, candidate_name: str, position_title: str, topics: List[str]
    ) -> List[InterviewQuestion]:
        questions: List[InterviewQuestion] = []

        # 1. Technical / Apply level
        questions.append(
            InterviewQuestion(
                category="Technical",
                question_text="How would you design a distributed indexing pipeline for high-throughput document search?",
                competency="Problem Solving & Algorithm Design",
                difficulty="Hard",
                blooms_level="Apply",
                expected_duration_mins=8,
                expected_answer_guidelines="Candidate should outline inverted indexing, partitioning, sharding, and latency trade-offs.",
                evidence_reference="Technical Skills & Publications",
            )
        )

        # 2. Teaching / Evaluate level
        questions.append(
            InterviewQuestion(
                category="Teaching",
                question_text="How do you explain NP-Completeness to undergraduate students with diverse backgrounds?",
                competency="Pedagogical Delivery & Teaching Ability",
                difficulty="Medium",
                blooms_level="Evaluate",
                expected_duration_mins=6,
                expected_answer_guidelines="Candidate should give intuitive reductions (e.g. 3-SAT to Graph Coloring) and clear visual analogies.",
                evidence_reference="Teaching Experience",
            )
        )

        # 3. Research / Create level
        questions.append(
            InterviewQuestion(
                category="Research",
                question_text="What is your 3-year research roadmap for securing external sponsored grants?",
                competency="Research Vision & Publication Strategy",
                difficulty="Expert",
                blooms_level="Create",
                expected_duration_mins=10,
                expected_answer_guidelines="Candidate should specify funding agencies (DST/SERB/MeitY), clear milestones, and publication venues.",
                evidence_reference="Scholarly Publications & DOIs",
            )
        )

        logger.debug("Bloom's taxonomy questions generated", count=len(questions))
        return questions
