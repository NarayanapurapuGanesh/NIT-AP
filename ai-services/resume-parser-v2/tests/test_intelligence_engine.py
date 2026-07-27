"""
Pytest Test Suite for Resume Intelligence Agent v2.0 (Enterprise Edition).

Tests Modules 1 through 13 end-to-end.
"""

import pytest
from validators.file_validator import FileValidator
from classifiers.type_detector import ResumeCategory, ResumeTypeDetector
from layout.layout_analyzer import LayoutAnalyzer
from extractors.deterministic_extractor import DeterministicExtractor
from extractors.link_discovery import ProfileLinkDiscoveryEngine
from services.profile_collector import ProfileCollectorService
from validators.profile_verifier import CandidateProfileVerifier
from validators.fraud_detector import ResumeFraudDetector
from validators.missing_info_evaluator import MissingInformationEvaluator
from llm.qwen_callback import QwenCallbackLLM
from quality.confidence_engine import ConfidenceEngine
from evidence.evidence_graph import EvidenceEngine
from services.candidate_intelligence_engine import CandidateIntelligenceEngine


@pytest.mark.asyncio
async def test_module1_file_validator():
    validator = FileValidator()

    # Valid PDF bytes header
    pdf_bytes = b"%PDF-1.7 sample content page..."
    res = validator.validate_file(pdf_bytes, "resume.pdf")
    assert res.is_valid is True
    assert res.file_extension == ".pdf"

    # Reject movie.mp4
    mp4_bytes = b"ftypisom..."
    res_mp4 = validator.validate_file(mp4_bytes, "movie.mp4")
    assert res_mp4.is_valid is False
    assert "Unsupported file format received: 'movie.mp4'" in res_mp4.error_message

    # Reject empty file
    res_empty = validator.validate_file(b"", "empty.pdf")
    assert res_empty.is_valid is False
    assert res_empty.is_corrupted is True


@pytest.mark.asyncio
async def test_module2_type_detector():
    detector = ResumeTypeDetector()

    # Image test
    img_res = detector.detect_type(b"", ".png")
    assert img_res.category == ResumeCategory.IMAGE_RESUME
    assert img_res.requires_ocr is True

    # Faculty CV test
    cv_text = "Curriculum Vitae. Dr. John Doe. Associate Professor. Department of Computer Science. Courses Taught. Publications. NSF Grant."
    cv_res = detector.detect_type(b"", ".pdf", extracted_text=cv_text)
    assert cv_res.category == ResumeCategory.FACULTY_CV
    assert cv_res.is_academic is True


@pytest.mark.asyncio
async def test_module3_deterministic_extractor():
    extractor = DeterministicExtractor()
    sample_text = """
    Dr. Jane Smith
    Email: jane.smith@university.edu
    Phone: +1 555-019-2831
    Skills: Python, PyTorch, FastApi, PostgreSQL, Machine Learning
    Education: Ph.D. in Computer Science from Stanford University (2020)
    Publications: Deep Learning in Academic Networks, IEEE 2021. DOI: 10.1109/54321
    """
    entities = extractor.extract_entities(sample_text)

    assert entities.name in {"Dr. Jane Smith", "Dr Jane Smith"}
    assert entities.email == "jane.smith@university.edu"
    assert entities.phone == "+1 555-019-2831"
    assert "Python" in entities.skills
    assert len(entities.education) >= 1
    assert "Ph.D" in entities.education[0].degree
    assert len(entities.publications) >= 1


@pytest.mark.asyncio
async def test_module5_and_6_link_discovery_and_collector():
    discovery = ProfileLinkDiscoveryEngine()
    text = "Check out my code at https://github.com/janesmith and publications on https://scholar.google.com/citations?user=123"
    links = discovery.discover_links(text)

    assert links.github == "https://github.com/janesmith"
    assert links.google_scholar is not None

    collector = ProfileCollectorService(offline_mode=True)
    evidence = await collector.collect_profiles(links)
    assert evidence.github is not None
    assert evidence.google_scholar is not None


@pytest.mark.asyncio
async def test_module7_verifier_and_module8_fraud():
    extractor = DeterministicExtractor()
    entities = extractor.extract_entities("Jane Smith")
    entities.skills = [f"Skill_{i}" for i in range(35)]

    fraud_detector = ResumeFraudDetector()
    fraud_rep = fraud_detector.analyze_fraud(entities)

    assert len(fraud_rep.indicators) >= 1
    assert fraud_rep.indicators[0].category == "SKILLS_INFLATION"


@pytest.mark.asyncio
async def test_module10_qwen_callback():
    qwen = QwenCallbackLLM()
    para = "Worked on high performance distributed deep learning training pipelines for vision foundation models."
    result = await qwen.classify_uncertain_paragraph(para)

    assert result.classification in {"Projects", "Research", "Skills", "Responsibilities"}


@pytest.mark.asyncio
async def test_full_candidate_intelligence_engine():
    engine = CandidateIntelligenceEngine(offline_mode=True)

    fake_pdf = b"%PDF-1.4\nDr. Alan Turing\nalan@turing.org\nSkills: Python, Cryptography\nEducation: Ph.D. Cambridge 1938\nGitHub: https://github.com/turing"
    profile = await engine.analyze_candidate_file(fake_pdf, "turing_cv.pdf")

    assert profile.file_meta.is_valid is True
    assert profile.candidate.email == "alan@turing.org"
    assert profile.confidence.overall_average > 50.0
    assert profile.evidence.total_evidence_nodes >= 1
