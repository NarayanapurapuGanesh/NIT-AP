"""
FacultyIQ Video Evidence Extraction Service — Summary Generator (Module 9).

Generates teaching summaries purely from extracted evidence (transcript + OCR)
using offline NLP techniques. No LLM, no cloud APIs.
"""

import re
from collections import Counter
from typing import List, Optional, Set

from app.core.logging import get_module_logger
from app.models.summary import TeachingSummary
from app.models.transcription import TranscriptionResult
from app.utils.file_utils import write_json
from app.services.ollama_client import OllamaClient
from app.models.dtos import SlideDTO
from app.utils.file_utils import write_json
from app.services.ollama_client import OllamaClient

log = get_module_logger("summary")

PROGRAMMING_LANGUAGES: Set[str] = {
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "ruby",
    "go", "rust", "swift", "kotlin", "scala", "perl", "php", "r", "matlab",
    "sql", "html", "css", "bash", "shell", "powershell", "lua", "haskell",
    "erlang", "elixir", "dart", "assembly", "fortran", "cobol", "lisp",
    "prolog", "scheme", "racket", "julia", "objective-c", "vhdl", "verilog",
}

ALGORITHM_KEYWORDS: Set[str] = {
    "binary search", "linear search", "bubble sort", "merge sort", "quick sort",
    "insertion sort", "selection sort", "heap sort", "radix sort", "counting sort",
    "dijkstra", "bellman-ford", "floyd-warshall", "kruskal", "prim",
    "breadth-first search", "bfs", "depth-first search", "dfs",
    "dynamic programming", "greedy algorithm", "backtracking", "divide and conquer",
    "recursion", "iteration", "hashing", "memoization", "tabulation",
    "graph traversal", "topological sort", "minimum spanning tree",
    "shortest path", "knapsack", "travelling salesman", "a* search",
    "neural network", "gradient descent", "k-means", "naive bayes",
    "decision tree", "random forest", "svm", "support vector machine",
    "regression", "classification", "clustering", "reinforcement learning",
}

TECHNICAL_DOMAINS: Set[str] = {
    "data structure", "algorithm", "database", "operating system", "network",
    "compiler", "machine learning", "artificial intelligence", "deep learning",
    "computer vision", "natural language processing", "cryptography",
    "distributed system", "cloud computing", "web development", "api",
    "microservice", "devops", "software engineering", "object oriented",
    "functional programming", "concurrency", "parallelism", "big data",
    "blockchain", "cybersecurity", "embedded system", "robotics",
    "computer architecture", "digital logic", "signal processing",
    "information theory", "automata theory", "complexity theory",
    "graph theory", "linear algebra", "probability", "statistics",
    "calculus", "discrete mathematics", "numerical methods",
}

STOP_WORDS: Set[str] = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "because", "but", "and", "or", "if", "while", "about", "also",
    "this", "that", "these", "those", "it", "its", "i", "me", "my", "we",
    "our", "you", "your", "he", "him", "his", "she", "her", "they", "them",
    "their", "what", "which", "who", "whom", "up", "down", "s", "t", "don",
    "re", "ve", "ll", "d", "m", "let", "us", "get", "got", "going", "go",
    "like", "know", "think", "want", "see", "look", "make", "say", "said",
    "one", "two", "three", "well", "okay", "right", "now", "today", "um",
    "uh", "yeah", "yes", "no", "actually", "basically", "really", "thing",
}


class SummaryGenerator:
    """Generates teaching summaries from extracted evidence using offline NLP."""

    def generate(
        self,
        transcription: Optional[TranscriptionResult],
        visuals: Optional[List[SlideDTO]],
        output_path: str,
        visuals_count: int = 0
    ) -> TeachingSummary:
        """Generates a teaching summary from transcript and OCR text."""
        log.info("Generating teaching summary from extracted evidence...")

        transcript_text = transcription.full_text if transcription else ""
        ocr_text = self._collect_ocr_text(visuals) if visuals else ""
        combined_text = f"{transcript_text} {ocr_text}".strip()

        if not combined_text:
            log.warning("No text evidence available. Proceeding to summary generator with empty context.")

        words = self._tokenize(combined_text)
        sentences = self._split_sentences(combined_text)

        short_summary = self._generate_short_summary(combined_text, len(transcript_text), len(ocr_text), visuals_count)
        topics = self._extract_topics(words, sentences)
        concepts = self._extract_concepts(words, combined_text)
        keywords = self._extract_keywords(words)
        technical_terms = self._extract_technical_terms(combined_text)
        programming_langs = self._extract_programming_languages(combined_text)
        algorithms = self._extract_algorithms(combined_text)
        subjects = self._extract_subjects(combined_text)

        summary = TeachingSummary(
            short_summary=short_summary,
            topics_covered=topics,
            concepts=concepts,
            keywords=keywords,
            technical_terms=technical_terms,
            programming_languages=programming_langs,
            algorithms=algorithms,
            subjects=subjects,
            json_path=output_path,
        )

        write_json(output_path, summary)

        log.info(
            "Summary generated: {} topics, {} keywords, {} technical terms",
            len(topics), len(keywords), len(technical_terms),
        )
        return summary

    def _collect_ocr_text(self, visuals: List[SlideDTO]) -> str:
        """Collects all OCR text from entries."""
        return " ".join(v.ocr_text for v in visuals if v.ocr_text)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes text into lowercase words."""
        return re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())

    def _split_sentences(self, text: str) -> List[str]:
        """Splits text into sentences."""
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    def _generate_short_summary(self, combined_text: str, transcript_len: int, ocr_len: int, visuals_count: int) -> str:
        """Generates a 2-3 sentence summary using the AI Orchestrator or fallback extraction."""
        if not combined_text and visuals_count == 0:
            return "No evidence extracted from video."
            
        try:
            client = OllamaClient()
            prompt = (
                "Summarize the following teaching demonstration transcript and OCR text into exactly 2-3 concise sentences. "
                "Focus on the main topics taught and the overall teaching style.\n\n"
                f"Evidence: {combined_text[:3000]}"
            )
            system_prompt = "You are a professional educational evaluator."
            prompt_size = len(prompt) + len(system_prompt)
            
            log.info(
                f"[PRE-OLLAMA] Agent: video | Prompt Size: {prompt_size} chars | "
                f"Transcript Len: {transcript_len} | OCR Len: {ocr_len} | Visuals: {visuals_count}"
            )
            
            response_data = client.chat(agent_name="video", prompt=prompt, system=system_prompt)
            summary_text = response_data.get("response", "")
            
            log.info(
                f"[POST-OLLAMA] Model: {response_data.get('model_used')} | "
                f"Time: {response_data.get('inference_time_seconds', 0):.2f}s | "
                f"Tokens: {response_data.get('tokens_generated', 0)}"
            )
            
            if summary_text:
                return summary_text.strip()
        except Exception as e:
            log.error(f"Failed to generate summary with Orchestrator: {e}. Falling back to offline extraction.")

        # Fallback to offline extraction
        sentences = self._split_sentences(combined_text)
        scored = []
        for sent in sentences:
            words = self._tokenize(sent)
            content_words = [w for w in words if w not in STOP_WORDS]
            score = len(content_words)

            for term in TECHNICAL_DOMAINS:
                if term in sent.lower():
                    score += 5
            for lang in PROGRAMMING_LANGUAGES:
                if lang in sent.lower():
                    score += 3

            scored.append((score, sent))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s for _, s in scored[:3]]

        summary = ". ".join(top_sentences)
        if not summary.endswith("."):
            summary += "."

        if len(summary) > 500:
            summary = summary[:497] + "..."

        return summary

    def _extract_topics(self, words: List[str], sentences: List[str]) -> List[str]:
        """Extracts main topics using noun-phrase frequency analysis."""
        bigrams = [
            f"{words[i]} {words[i + 1]}"
            for i in range(len(words) - 1)
            if words[i] not in STOP_WORDS and words[i + 1] not in STOP_WORDS
        ]
        counter = Counter(bigrams)
        topics = [phrase.title() for phrase, count in counter.most_common(10) if count >= 2]
        return topics[:10]

    def _extract_concepts(self, words: List[str], text: str) -> List[str]:
        """Extracts key concepts from technical domain matching."""
        concepts: List[str] = []
        text_lower = text.lower()
        for domain in TECHNICAL_DOMAINS:
            if domain in text_lower:
                concepts.append(domain.title())
        return sorted(set(concepts))[:15]

    def _extract_keywords(self, words: List[str]) -> List[str]:
        """Extracts top keywords by frequency, excluding stop words."""
        content_words = [w for w in words if w not in STOP_WORDS and len(w) > 3]
        counter = Counter(content_words)
        return [word for word, _ in counter.most_common(20)]

    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extracts technical terms found in the domain vocabulary."""
        terms: List[str] = []
        text_lower = text.lower()
        for domain in TECHNICAL_DOMAINS:
            if domain in text_lower:
                terms.append(domain.title())
        return sorted(set(terms))[:20]

    def _extract_programming_languages(self, text: str) -> List[str]:
        """Extracts programming languages mentioned in the text."""
        found: List[str] = []
        text_lower = text.lower()
        for lang in PROGRAMMING_LANGUAGES:
            pattern = rf"\b{re.escape(lang)}\b"
            if re.search(pattern, text_lower):
                found.append(lang.title() if len(lang) > 2 else lang.upper())
        return sorted(set(found))

    def _extract_algorithms(self, text: str) -> List[str]:
        """Extracts algorithm names mentioned in the text."""
        found: List[str] = []
        text_lower = text.lower()
        for algo in ALGORITHM_KEYWORDS:
            if algo in text_lower:
                found.append(algo.title())
        return sorted(set(found))

    def _extract_subjects(self, text: str) -> List[str]:
        """Extracts academic subjects from the text."""
        subject_patterns = [
            r"\b(computer science|mathematics|physics|chemistry|biology|"
            r"engineering|statistics|economics|philosophy|psychology|"
            r"data science|information technology|electrical engineering|"
            r"mechanical engineering|civil engineering|software engineering|"
            r"artificial intelligence|machine learning|cybersecurity)\b"
        ]
        subjects: List[str] = []
        text_lower = text.lower()
        for pattern in subject_patterns:
            matches = re.findall(pattern, text_lower)
            subjects.extend(m.title() for m in matches)
        return sorted(set(subjects))
