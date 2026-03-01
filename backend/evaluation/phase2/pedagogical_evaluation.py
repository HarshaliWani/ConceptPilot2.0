"""
PHASE 2: Simulated Pedagogical Evaluation Framework
==================================================

LLM-as-Judge + Manual Review System for Quiz/Flashcard Quality Assessment
Research validation without human studies - uses GPT-4/Claude for content evaluation.
"""

import asyncio
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.services.quiz_generator import generate_quiz
from app.services.flashcard_generator import generate_flashcards
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.core.config import get_settings

settings = get_settings()


class PedagogicalRubric:
    """Standardized rubrics for educational content evaluation."""
    
    QUIZ_RUBRIC = {
        "correctness": {
            "description": "Accuracy of correct answers and scientific validity",
            "criteria": {
                5: "Completely accurate, scientifically precise, no errors",
                4: "Mostly accurate, minor imprecision acceptable for level", 
                3: "Generally correct, some minor conceptual issues",
                2: "Major accuracy issues, but core concept present",
                1: "Significant errors, misleading or incorrect information"
            }
        },
        "distractor_quality": {
            "description": "Quality of incorrect answer choices (plausible, educational)",
            "criteria": {
                5: "Highly plausible distractors that reveal common misconceptions",
                4: "Good distractors, mostly plausible with educational value",
                3: "Adequate distractors, some reveal misconceptions", 
                2: "Weak distractors, too obvious or poorly constructed",
                1: "Poor distractors, clearly wrong or nonsensical"
            }
        },
        "difficulty_appropriateness": {
            "description": "Appropriate challenge level for target audience",
            "criteria": {
                5: "Perfect difficulty match for specified grade/proficiency level",
                4: "Appropriate difficulty, minor calibration issues",
                3: "Generally appropriate, some items too hard/easy",
                2: "Noticeable difficulty mismatch for target audience", 
                1: "Severely inappropriate difficulty level"
            }
        },
        "clarity": {
            "description": "Question clarity and lack of ambiguity",
            "criteria": {
                5: "Crystal clear, unambiguous, well-worded questions",
                4: "Clear questions with minimal ambiguity",
                3: "Generally clear, some minor wording issues",
                2: "Some ambiguous or confusing elements",
                1: "Confusing, ambiguous, or poorly worded questions"
            }
        },
        "pedagogical_value": {
            "description": "Educational effectiveness and learning alignment",
            "criteria": {
                5: "Excellent learning objectives, promotes deep understanding",
                4: "Good educational value, supports learning goals", 
                3: "Adequate pedagogical value, basic learning support",
                2: "Limited educational value, superficial assessment",
                1: "Poor pedagogical design, little learning value"
            }
        }
    }
    
    FLASHCARD_RUBRIC = {
        "content_accuracy": {
            "description": "Factual correctness and scientific precision",
            "criteria": {
                5: "Completely accurate, precise, authoritative content",
                4: "Accurate with appropriate level of detail",
                3: "Generally accurate, minor oversimplification acceptable",
                2: "Some accuracy issues, but concepts mostly correct",
                1: "Significant inaccuracies or misleading information"
            }
        },
        "cognitive_load": {
            "description": "Appropriate information density for flashcard format",
            "criteria": {
                5: "Perfect information chunking, optimal cognitive load",
                4: "Good information density, easily digestible",
                3: "Appropriate amount of information, manageable load",
                2: "Slightly too much/little information for flashcards",
                1: "Poor information density, cognitive overload or underload"
            }
        },
        "memorability": {
            "description": "Use of effective memory techniques and mnemonics",
            "criteria": {
                5: "Excellent use of memory techniques, highly memorable",
                4: "Good memory aids, effective recall strategies",
                3: "Some memory support, basic mnemonic value",
                2: "Limited memory support, relies mainly on repetition",
                1: "Poor memorability, difficult to retain information"
            }
        },
        "contextual_relevance": {
            "description": "Connection to real-world applications and examples",
            "criteria": {
                5: "Excellent real-world connections, highly relevant examples",
                4: "Good contextual examples, clear relevance",
                3: "Some context provided, adequate real-world links",
                2: "Limited contextual relevance, mostly abstract",
                1: "No meaningful context, purely theoretical content"
            }
        },
        "progressive_difficulty": {
            "description": "Appropriate scaffolding and difficulty progression",
            "criteria": {
                5: "Perfect difficulty progression, excellent scaffolding",
                4: "Good progression, supports skill building",
                3: "Adequate progression, some scaffolding present",
                2: "Inconsistent difficulty, limited scaffolding",
                1: "Poor progression, difficulty jumps or gaps"
            }
        }
    }


class LLMJudge:
    """LLM-powered evaluation of educational content quality."""
    
    def __init__(self):
        self.llm = None
        self.setup_llm()
    
    def setup_llm(self):
        """Initialize LLM for evaluation.""" 
        groq_key = settings.groq_api_key
        if groq_key:
            try:
                self.llm = ChatGroq(
                    model="llama3-groq-70b-8192-tool-use-preview",
                    temperature=0.3,  # Lower temperature for more consistent evaluation
                    groq_api_key=groq_key,
                )
            except Exception as e:
                print(f"[LLMJudge] Failed to initialize Groq: {e}")
    
    async def evaluate_quiz(self, quiz_data: Dict[str, Any], rubric_category: str = "all") -> Dict[str, Any]:
        """Evaluate a quiz using LLM-as-judge methodology."""
        
        if not self.llm:
            return {"error": "No LLM available for evaluation"}
        
        # Create evaluation prompt
        evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educational assessment evaluator. Your task is to critically analyze quiz questions using standardized pedagogical rubrics.

EVALUATION RUBRICS (1-5 scale):

CORRECTNESS (1-5):
5 = Completely accurate, scientifically precise, no errors
4 = Mostly accurate, minor imprecision acceptable for level  
3 = Generally correct, some minor conceptual issues
2 = Major accuracy issues, but core concept present
1 = Significant errors, misleading or incorrect information

DISTRACTOR QUALITY (1-5):
5 = Highly plausible distractors that reveal common misconceptions
4 = Good distractors, mostly plausible with educational value
3 = Adequate distractors, some reveal misconceptions
2 = Weak distractors, too obvious or poorly constructed  
1 = Poor distractors, clearly wrong or nonsensical

DIFFICULTY APPROPRIATENESS (1-5):
5 = Perfect difficulty match for specified grade/proficiency level
4 = Appropriate difficulty, minor calibration issues
3 = Generally appropriate, some items too hard/easy
2 = Noticeable difficulty mismatch for target audience
1 = Severely inappropriate difficulty level

CLARITY (1-5):
5 = Crystal clear, unambiguous, well-worded questions
4 = Clear questions with minimal ambiguity
3 = Generally clear, some minor wording issues
2 = Some ambiguous or confusing elements
1 = Confusing, ambiguous, or poorly worded questions

PEDAGOGICAL VALUE (1-5):
5 = Excellent learning objectives, promotes deep understanding
4 = Good educational value, supports learning goals
3 = Adequate pedagogical value, basic learning support  
2 = Limited educational value, superficial assessment
1 = Poor pedagogical design, little learning value

EVALUATION REQUIREMENTS:
- Provide scores for each rubric dimension (1-5)
- Give specific justifications for each score
- Identify strengths and areas for improvement
- Consider the target audience specified
- Be objective and constructive in feedback

OUTPUT FORMAT:
{{
  "correctness": {{"score": X, "justification": "..."}},
  "distractor_quality": {{"score": X, "justification": "..."}},
  "difficulty_appropriateness": {{"score": X, "justification": "..."}}, 
  "clarity": {{"score": X, "justification": "..."}},
  "pedagogical_value": {{"score": X, "justification": "..."}},
  "overall_score": X.X,
  "strengths": ["...", "..."],
  "areas_for_improvement": ["...", "..."],
  "recommendation": "..."
}}"""),
            
            ("user", """Evaluate this quiz question:

TOPIC: {topic}
TARGET AUDIENCE: {grade_level}, {proficiency_level} level
CONTEXT: Tailored to student interest in {user_interest}

QUESTION: {question_text}

CORRECT ANSWER: {correct_answer}

INCORRECT OPTIONS:
{incorrect_options}

EXPLANATION: {explanation}

Please evaluate this quiz question against all five rubric dimensions and provide detailed feedback.""")
        ])
        
        try:
            # Extract quiz question data
            if "questions" in quiz_data and len(quiz_data["questions"]) > 0:
                question = quiz_data["questions"][0]  # Evaluate first question
                
                # Format incorrect options
                incorrect_opts = []
                for i, opt in enumerate(question.get("options", [])):
                    if i != question.get("correct_answer", 0):
                        incorrect_opts.append(f"- {opt}")
                
                chain = evaluation_prompt | self.llm
                response = await chain.ainvoke({
                    "topic": quiz_data.get("topic", "Unknown"),
                    "grade_level": quiz_data.get("grade_level", "Unknown"),
                    "proficiency_level": quiz_data.get("proficiency_level", "Unknown"), 
                    "user_interest": quiz_data.get("tailored_to_interest", "Unknown"),
                    "question_text": question.get("question", "No question text"),
                    "correct_answer": question.get("options", ["Missing"])[question.get("correct_answer", 0)] if question.get("options") else "Missing",
                    "incorrect_options": "\n".join(incorrect_opts) if incorrect_opts else "No incorrect options",
                    "explanation": question.get("explanation", "No explanation provided")
                })
                
                # Parse response
                if hasattr(response, "content"):
                    content = response.content
                else:
                    content = response
                
                # Try to extract JSON from response
                if isinstance(content, str):
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:-3]
                    elif content.startswith("```"):
                        content = content[3:-3]
                    
                    if not content.startswith("{"):
                        content = "{" + content
                    
                    try:
                        evaluation_result = json.loads(content)
                        evaluation_result["evaluation_timestamp"] = datetime.utcnow().isoformat()
                        evaluation_result["evaluator"] = "llm_judge_groq"
                        return evaluation_result
                    except json.JSONDecodeError:
                        return {
                            "error": "Failed to parse LLM evaluation response",
                            "raw_response": content[:500]
                        }
                
                return evaluation_result if isinstance(content, dict) else {"error": "Unexpected response format"}
                
            else:
                return {"error": "No questions found in quiz data"}
                
        except Exception as e:
            return {"error": f"LLM evaluation failed: {str(e)}"}
    
    async def evaluate_flashcard_set(self, flashcard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate flashcards using LLM-as-judge methodology."""
        
        if not self.llm:
            return {"error": "No LLM available for evaluation"}
        
        evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educational content evaluator specializing in flashcard effectiveness. Evaluate flashcard sets using standardized pedagogical rubrics.

FLASHCARD EVALUATION RUBRICS (1-5 scale):

CONTENT ACCURACY (1-5):
5 = Completely accurate, precise, authoritative content
4 = Accurate with appropriate level of detail
3 = Generally accurate, minor oversimplification acceptable
2 = Some accuracy issues, but concepts mostly correct
1 = Significant inaccuracies or misleading information

COGNITIVE LOAD (1-5):
5 = Perfect information chunking, optimal cognitive load
4 = Good information density, easily digestible  
3 = Appropriate amount of information, manageable load
2 = Slightly too much/little information for flashcards
1 = Poor information density, cognitive overload or underload

MEMORABILITY (1-5):
5 = Excellent use of memory techniques, highly memorable
4 = Good memory aids, effective recall strategies
3 = Some memory support, basic mnemonic value
2 = Limited memory support, relies mainly on repetition
1 = Poor memorability, difficult to retain information

CONTEXTUAL RELEVANCE (1-5):
5 = Excellent real-world connections, highly relevant examples
4 = Good contextual examples, clear relevance
3 = Some context provided, adequate real-world links
2 = Limited contextual relevance, mostly abstract
1 = No meaningful context, purely theoretical content

PROGRESSIVE DIFFICULTY (1-5):
5 = Perfect difficulty progression, excellent scaffolding
4 = Good progression, supports skill building
3 = Adequate progression, some scaffolding present
2 = Inconsistent difficulty, limited scaffolding
1 = Poor progression, difficulty jumps or gaps

OUTPUT FORMAT:
{{
  "content_accuracy": {{"score": X, "justification": "..."}},
  "cognitive_load": {{"score": X, "justification": "..."}},
  "memorability": {{"score": X, "justification": "..."}},
  "contextual_relevance": {{"score": X, "justification": "..."}},
  "progressive_difficulty": {{"score": X, "justification": "..."}},
  "overall_score": X.X,
  "strengths": ["...", "..."],
  "areas_for_improvement": ["...", "..."],
  "recommendation": "..."
}}"""),
            
            ("user", """Evaluate this flashcard set:

TOPIC: {topic}
TARGET AUDIENCE: {grade_level}, {proficiency_level} level
CONTEXT: Tailored to student interest in {user_interest}

FLASHCARD SET ({card_count} cards):
{flashcard_content}

Please evaluate this flashcard set against all five rubric dimensions and provide detailed feedback.""")
        ])
        
        try:
            # Format flashcard content for evaluation
            cards = flashcard_data.get("flashcards", [])
            card_content = []
            
            for i, card in enumerate(cards[:5]):  # Sample first 5 cards
                card_content.append(f"Card {i+1}:")
                card_content.append(f"  Front: {card.get('front', 'Missing front')}")
                card_content.append(f"  Back: {card.get('back', 'Missing back')}")
                card_content.append("")
            
            chain = evaluation_prompt | self.llm
            response = await chain.ainvoke({
                "topic": flashcard_data.get("topic", "Unknown"),
                "grade_level": flashcard_data.get("grade_level", "Unknown"), 
                "proficiency_level": flashcard_data.get("proficiency_level", "Unknown"),
                "user_interest": flashcard_data.get("tailored_to_interest", "Unknown"),
                "card_count": len(cards),
                "flashcard_content": "\n".join(card_content)
            })
            
            # Parse response (similar to quiz evaluation)
            if hasattr(response, "content"):
                content = response.content
            else:
                content = response
            
            if isinstance(content, str):
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:-3]
                elif content.startswith("```"):
                    content = content[3:-3]
                
                if not content.startswith("{"):
                    content = "{" + content
                
                try:
                    evaluation_result = json.loads(content)
                    evaluation_result["evaluation_timestamp"] = datetime.utcnow().isoformat()
                    evaluation_result["evaluator"] = "llm_judge_groq"
                    return evaluation_result
                except json.JSONDecodeError:
                    return {
                        "error": "Failed to parse LLM evaluation response",
                        "raw_response": content[:500]
                    }
            
            return evaluation_result if isinstance(content, dict) else {"error": "Unexpected response format"}
            
        except Exception as e:
            return {"error": f"LLM evaluation failed: {str(e)}"}


class ManualReviewInterface:
    """Interface for manual review and scoring."""
    
    def __init__(self):
        self.review_data = []
    
    def generate_review_template(self, content_type: str, items: List[Dict]) -> Dict[str, Any]:
        """Generate a review template for manual evaluation."""
        
        template = {
            "review_metadata": {
                "content_type": content_type,
                "total_items": len(items),
                "review_date": datetime.utcnow().isoformat(),
                "reviewer": "manual_reviewer",
                "estimated_time": f"{len(items) * 6} minutes"  # 6 min per item average
            },
            "rubric": PedagogicalRubric.QUIZ_RUBRIC if content_type == "quiz" else PedagogicalRubric.FLASHCARD_RUBRIC,
            "items_for_review": []
        }
        
        for i, item in enumerate(items):
            review_item = {
                "item_id": i + 1,
                "content": item,
                "manual_scores": {
                    rubric_dim: {
                        "score": None,  # To be filled by reviewer
                        "notes": "",
                        "confidence": None  # 1-5 confidence in score
                    }
                    for rubric_dim in template["rubric"].keys()
                },
                "overall_assessment": {
                    "overall_score": None,
                    "recommendation": "",
                    "time_spent_minutes": None,
                    "reviewer_comments": ""
                }
            }
            template["items_for_review"].append(review_item)
        
        return template
    
    def calculate_manual_review_stats(self, completed_reviews: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics from completed manual reviews."""
        
        if not completed_reviews:
            return {"error": "No completed reviews provided"}
        
        stats = {
            "total_reviews": len(completed_reviews),
            "rubric_scores": {},
            "overall_scores": [],
            "review_times": [],
            "inter_rater_reliability": None,
            "common_issues": [],
            "reviewer_feedback": []
        }
        
        # Extract all scores by rubric dimension
        all_rubric_dims = set()
        for review in completed_reviews:
            if "manual_scores" in review:
                all_rubric_dims.update(review["manual_scores"].keys())
        
        for dim in all_rubric_dims:
            scores = []
            for review in completed_reviews:
                if "manual_scores" in review and dim in review["manual_scores"]:
                    score = review["manual_scores"][dim].get("score")
                    if score is not None:
                        scores.append(score)
            
            if scores:
                stats["rubric_scores"][dim] = {
                    "mean": statistics.mean(scores),
                    "median": statistics.median(scores),
                    "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                    "min": min(scores),
                    "max": max(scores),
                    "count": len(scores)
                }
        
        # Overall assessment scores
        overall_scores = []
        for review in completed_reviews:
            if "overall_assessment" in review:
                score = review["overall_assessment"].get("overall_score")
                if score is not None:
                    overall_scores.append(score)
        
        if overall_scores:
            stats["overall_scores"] = {
                "mean": statistics.mean(overall_scores),
                "median": statistics.median(overall_scores),
                "std_dev": statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0,
                "distribution": {i: overall_scores.count(i) for i in range(1, 6)}
            }
        
        return stats


async def run_pedagogical_evaluation(
    num_quizzes: int = 20,
    num_flashcard_sets: int = 10,
    manual_review_count: int = 10
) -> Dict[str, Any]:
    """
    Run comprehensive pedagogical evaluation with LLM judges and manual review.
    
    Phase 2 of the research evaluation framework.
    """
    
    print("🎓 PHASE 2: Simulated Pedagogical Evaluation")
    print("=" * 50)
    print(f"📊 Plan:")
    print(f"   • LLM-judge evaluation of {num_quizzes} quizzes")
    print(f"   • LLM-judge evaluation of {num_flashcard_sets} flashcard sets")
    print(f"   • Manual review framework for {manual_review_count} items")
    print(f"   • Rubric-based scoring (1-5 scale)")
    print()
    
    # Initialize components
    llm_judge = LLMJudge()
    manual_reviewer = ManualReviewInterface()
    
    # Create results directory
    results_dir = Path("../../evaluation_results/phase2")
    results_dir.mkdir(exist_ok=True, parents=True)
    
    # Phase 2A: Generate and evaluate quizzes
    print("📝 Phase 2A: Quiz Generation & LLM Evaluation")
    quiz_evaluations = []
    
    # STEM topics for quiz generation (subset from Phase 1)
    quiz_topics = [
        "Quadratic Equations", "Newton's Laws of Motion", "Ohm's Law Applications",
        "Calculus Derivatives", "Electromagnetic Induction", "Digital Logic Gates",
        "Probability Theory", "Wave Properties", "AC vs DC Current",
        "Linear Algebra", "Thermodynamics", "Capacitors and Inductors",
        "Trigonometry", "Quantum Mechanics", "Circuit Analysis",
        "Statistics", "Optics and Refraction", "Transistor Operation",
        "Geometry Proofs", "Energy Conservation"
    ]
    
    user_interests = ["technology", "games", "sports", "music", "science"]
    proficiency_levels = ["beginner", "intermediate", "advanced"]
    grade_levels = ["middle school", "high school", "college"]
    
    print(f"⏳ Generating and evaluating {num_quizzes} quizzes...")
    
    for i in range(num_quizzes):
        topic = quiz_topics[i % len(quiz_topics)]
        user_interest = user_interests[i % len(user_interests)]
        proficiency = proficiency_levels[i % len(proficiency_levels)]
        grade = grade_levels[i % len(grade_levels)]
        
        try:
            # Generate quiz
            quiz_data = await generate_quiz(
                topic=topic,
                topic_description=f"Generate quiz for {proficiency} level {grade} students interested in {user_interest}",
                num_questions=5  # Smaller number for evaluation purposes
            )
            
            # Evaluate with LLM judge
            llm_evaluation = await llm_judge.evaluate_quiz(quiz_data)
            
            quiz_evaluations.append({
                "quiz_id": i + 1,
                "generation_params": {
                    "topic": topic,
                    "user_interest": user_interest,
                    "proficiency_level": proficiency,
                    "grade_level": grade
                },
                "quiz_data": quiz_data,
                "llm_evaluation": llm_evaluation,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            print(f"\r   Quiz {i+1}/{num_quizzes}: {topic[:25]}... ", end="", flush=True)
            
        except Exception as e:
            print(f"\n   ❌ Failed to generate/evaluate quiz {i+1}: {e}")
    
    print("\n✅ Quiz evaluation completed!")
    
    # Phase 2B: Generate and evaluate flashcards
    print(f"\n🗃️ Phase 2B: Flashcard Generation & LLM Evaluation")
    flashcard_evaluations = []
    
    print(f"⏳ Generating and evaluating {num_flashcard_sets} flashcard sets...")
    
    for i in range(num_flashcard_sets):
        topic = quiz_topics[i % len(quiz_topics)]
        user_interest = user_interests[i % len(user_interests)]
        proficiency = proficiency_levels[i % len(proficiency_levels)]
        grade = grade_levels[i % len(grade_levels)]
        
        try:
            # Generate flashcards
            flashcard_raw_data = await generate_flashcards(
                topic=f"{topic} for {proficiency} level {grade} students interested in {user_interest}",
                count=8  # Reasonable number for evaluation
            )
            
            # Wrap flashcard data in evaluation structure
            flashcard_data = {
                "topic": topic,
                "flashcards": flashcard_raw_data,
                "grade_level": grade,
                "proficiency_level": proficiency,
                "tailored_to_interest": user_interest
            }
            
            # Evaluate with LLM judge  
            llm_evaluation = await llm_judge.evaluate_flashcard_set(flashcard_data)
            
            flashcard_evaluations.append({
                "flashcard_set_id": i + 1,
                "generation_params": {
                    "topic": topic,
                    "user_interest": user_interest,
                    "proficiency_level": proficiency,
                    "grade_level": grade
                },
                "flashcard_data": flashcard_data,
                "llm_evaluation": llm_evaluation,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            print(f"\r   Flashcard set {i+1}/{num_flashcard_sets}: {topic[:20]}... ", end="", flush=True)
            
        except Exception as e:
            print(f"\n   ❌ Failed to generate/evaluate flashcard set {i+1}: {e}")
    
    print("\n✅ Flashcard evaluation completed!")
    
    # Phase 2C: Manual review framework
    print(f"\n👥 Phase 2C: Manual Review Framework Setup")
    
    # Select items for manual review (mix of quizzes and flashcards)
    manual_review_items = []
    
    # Add quiz items for manual review
    quiz_sample_size = min(manual_review_count // 2, len(quiz_evaluations))
    for i in range(quiz_sample_size):
        manual_review_items.append({
            "type": "quiz",
            "data": quiz_evaluations[i]
        })
    
    # Add flashcard items for manual review
    flashcard_sample_size = manual_review_count - quiz_sample_size
    for i in range(min(flashcard_sample_size, len(flashcard_evaluations))):
        manual_review_items.append({
            "type": "flashcard",
            "data": flashcard_evaluations[i]
        })
    
    # Generate manual review templates
    quiz_review_template = manual_reviewer.generate_review_template(
        "quiz", 
        [item["data"] for item in manual_review_items if item["type"] == "quiz"]
    )
    
    flashcard_review_template = manual_reviewer.generate_review_template(
        "flashcard",
        [item["data"] for item in manual_review_items if item["type"] == "flashcard"]
    )
    
    print(f"✅ Manual review framework created!")
    print(f"   • Quiz review template: {len(quiz_review_template['items_for_review'])} items")
    print(f"   • Flashcard review template: {len(flashcard_review_template['items_for_review'])} items")
    print(f"   • Estimated review time: {(len(manual_review_items) * 6)} minutes")
    
    # Compile results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    pedagogical_evaluation_results = {
        "evaluation_metadata": {
            "phase": "Phase 2: Simulated Pedagogical Evaluation",
            "evaluation_date": datetime.utcnow().isoformat(),
            "num_quizzes_evaluated": len(quiz_evaluations),
            "num_flashcard_sets_evaluated": len(flashcard_evaluations),
            "num_manual_review_items": len(manual_review_items),
            "llm_judge_model": "llama3-groq-70b-8192-tool-use-preview"
        },
        "quiz_evaluations": quiz_evaluations,
        "flashcard_evaluations": flashcard_evaluations,
        "manual_review_templates": {
            "quiz_template": quiz_review_template,
            "flashcard_template": flashcard_review_template
        },
        "rubrics": {
            "quiz_rubric": PedagogicalRubric.QUIZ_RUBRIC,
            "flashcard_rubric": PedagogicalRubric.FLASHCARD_RUBRIC
        }
    }
    
    # Save detailed results
    with open(results_dir / f"pedagogical_evaluation_{timestamp}.json", "w") as f:
        json.dump(pedagogical_evaluation_results, f, indent=2)
    
    # Save manual review templates separately for easy access
    with open(results_dir / f"manual_review_quiz_template_{timestamp}.json", "w") as f:
        json.dump(quiz_review_template, f, indent=2)
        
    with open(results_dir / f"manual_review_flashcard_template_{timestamp}.json", "w") as f:
        json.dump(flashcard_review_template, f, indent=2)
    
    # Generate summary report
    generate_pedagogical_summary_report(pedagogical_evaluation_results, results_dir / f"pedagogical_summary_{timestamp}.txt")
    
    print(f"\n📁 Results saved to: {results_dir}")
    print(f"   - Full evaluation: pedagogical_evaluation_{timestamp}.json")
    print(f"   - Quiz review template: manual_review_quiz_template_{timestamp}.json")
    print(f"   - Flashcard review template: manual_review_flashcard_template_{timestamp}.json")
    print(f"   - Summary report: pedagogical_summary_{timestamp}.txt")
    
    return pedagogical_evaluation_results


def generate_pedagogical_summary_report(results: Dict[str, Any], output_path: Path):
    """Generate human-readable pedagogical evaluation summary."""
    
    with open(output_path, "w") as f:
        f.write("PEDAGOGICAL EVALUATION SUMMARY REPORT\n")
        f.write("=" * 45 + "\n\n")
        
        metadata = results["evaluation_metadata"]
        f.write(f"Evaluation Date: {datetime.fromisoformat(metadata['evaluation_date']).strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Phase: {metadata['phase']}\n")
        f.write(f"LLM Judge Model: {metadata['llm_judge_model']}\n\n")
        
        # Quiz evaluation summary
        f.write("QUIZ EVALUATION SUMMARY\n")
        f.write("-" * 25 + "\n")
        
        quiz_evals = results["quiz_evaluations"]
        f.write(f"Total Quizzes Evaluated: {len(quiz_evals)}\n")
        
        if quiz_evals:
            # Calculate LLM judge statistics for quizzes
            successful_quiz_evals = [q for q in quiz_evals if "error" not in q.get("llm_evaluation", {})]
            f.write(f"Successful LLM Evaluations: {len(successful_quiz_evals)}/{len(quiz_evals)}\n")
            
            if successful_quiz_evals:
                # Extract scores
                rubric_scores = {}
                overall_scores = []
                
                for eval_data in successful_quiz_evals:
                    llm_eval = eval_data["llm_evaluation"]
                    if "overall_score" in llm_eval:
                        overall_scores.append(float(llm_eval["overall_score"]))
                    
                    for rubric_dim in ["correctness", "distractor_quality", "difficulty_appropriateness", "clarity", "pedagogical_value"]:
                        if rubric_dim in llm_eval and "score" in llm_eval[rubric_dim]:
                            if rubric_dim not in rubric_scores:
                                rubric_scores[rubric_dim] = []
                            rubric_scores[rubric_dim].append(llm_eval[rubric_dim]["score"])
                
                if overall_scores:
                    f.write(f"Average Overall Score: {statistics.mean(overall_scores):.2f}/5.0\n")
                    f.write(f"Score Range: {min(overall_scores):.1f} - {max(overall_scores):.1f}\n")
                
                f.write("\nRubric Dimension Scores:\n")
                for dim, scores in rubric_scores.items():
                    if scores:
                        f.write(f"  {dim.replace('_', ' ').title()}: {statistics.mean(scores):.2f}/5.0 (σ={statistics.stdev(scores):.2f})\n")
        
        # Flashcard evaluation summary
        f.write(f"\nFLASHCARD EVALUATION SUMMARY\n")
        f.write("-" * 30 + "\n")
        
        flashcard_evals = results["flashcard_evaluations"]
        f.write(f"Total Flashcard Sets Evaluated: {len(flashcard_evals)}\n")
        
        if flashcard_evals:
            successful_flashcard_evals = [f for f in flashcard_evals if "error" not in f.get("llm_evaluation", {})]
            f.write(f"Successful LLM Evaluations: {len(successful_flashcard_evals)}/{len(flashcard_evals)}\n")
            
            if successful_flashcard_evals:
                # Extract scores
                rubric_scores = {}
                overall_scores = []
                
                for eval_data in successful_flashcard_evals:
                    llm_eval = eval_data["llm_evaluation"]
                    if "overall_score" in llm_eval:
                        overall_scores.append(float(llm_eval["overall_score"]))
                    
                    for rubric_dim in ["content_accuracy", "cognitive_load", "memorability", "contextual_relevance", "progressive_difficulty"]:
                        if rubric_dim in llm_eval and "score" in llm_eval[rubric_dim]:
                            if rubric_dim not in rubric_scores:
                                rubric_scores[rubric_dim] = []
                            rubric_scores[rubric_dim].append(llm_eval[rubric_dim]["score"])
                
                if overall_scores:
                    f.write(f"Average Overall Score: {statistics.mean(overall_scores):.2f}/5.0\n")
                    f.write(f"Score Range: {min(overall_scores):.1f} - {max(overall_scores):.1f}\n")
                
                f.write("\nRubric Dimension Scores:\n")
                for dim, scores in rubric_scores.items():
                    if scores:
                        f.write(f"  {dim.replace('_', ' ').title()}: {statistics.mean(scores):.2f}/5.0 (σ={statistics.stdev(scores):.2f})\n")
        
        # Manual review information
        f.write(f"\nMANUAL REVIEW FRAMEWORK\n")
        f.write("-" * 25 + "\n")
        
        quiz_template = results["manual_review_templates"]["quiz_template"]
        flashcard_template = results["manual_review_templates"]["flashcard_template"]
        
        f.write(f"Quiz Items for Manual Review: {len(quiz_template['items_for_review'])}\n")
        f.write(f"Flashcard Items for Manual Review: {len(flashcard_template['items_for_review'])}\n")
        f.write(f"Estimated Review Time: {quiz_template['review_metadata']['estimated_time']} + {flashcard_template['review_metadata']['estimated_time']}\n")
        
        f.write(f"\nNext Steps for Manual Review:\n")
        f.write(f"1. Open manual review JSON templates\n")
        f.write(f"2. Score each item using 1-5 rubric scales\n")
        f.write(f"3. Add reviewer comments and confidence ratings\n")
        f.write(f"4. Return completed templates for analysis\n")


if __name__ == "__main__":
    print("Phase 2: Pedagogical Evaluation Framework")
    print("Starting evaluation in 3 seconds...")
    
    async def main():
        try:
            results = await run_pedagogical_evaluation(
                num_quizzes=20,
                num_flashcard_sets=10, 
                manual_review_count=10
            )
            print("\n🎉 Pedagogical evaluation completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Evaluation failed: {e}")
            raise
    
    asyncio.run(main())