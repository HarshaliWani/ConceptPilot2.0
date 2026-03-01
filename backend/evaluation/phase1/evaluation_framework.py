"""
Comprehensive Evaluation Framework for Lesson Generation System
============================================================

This script generates 100 lessons across 20 STEM topics and performs automated
validation with technical metrics for research evaluation.
"""

import asyncio
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path

from app.services.lesson_generator import generate_lesson


# 20 STEM Topics across Math, Physics, and Circuits
STEM_TOPICS = {
    "Mathematics": [
        "Quadratic Equations",
        "Calculus Derivatives", 
        "Probability Theory",
        "Linear Algebra",
        "Trigonometry",
        "Statistics and Data Analysis",
        "Geometry Proofs"
    ],
    "Physics": [
        "Newton's Laws of Motion",
        "Electromagnetic Induction",
        "Wave Properties and Interference", 
        "Thermodynamics First Law",
        "Quantum Mechanics Basics",
        "Optics and Refraction",
        "Energy Conservation"
    ],
    "Circuits": [
        "Ohm's Law Applications",
        "AC vs DC Current",
        "Capacitors and Inductors",
        "Digital Logic Gates",
        "Transistor Operation",
        "Circuit Analysis Methods"
    ]
}

# User interests to diversify lessons
USER_INTERESTS = [
    "video games", "sports", "music", "cooking", "art", "technology", 
    "nature", "space", "movies", "cars", "fashion", "animals"
]

PROFICIENCY_LEVELS = ["beginner", "intermediate", "advanced"]
GRADE_LEVELS = ["middle school", "high school", "college"]


class LessonValidator:
    """Validates lesson content quality and structure."""
    
    @staticmethod
    def validate_lesson_structure(lesson: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required fields and data types."""
        validation_results = {
            "has_required_fields": True,
            "field_errors": [],
            "structure_score": 0
        }
        
        required_fields = [
            "topic", "title", "narration_script", 
            "board_actions", "duration", "tailored_to_interest"
        ]
        
        for field in required_fields:
            if field not in lesson:
                validation_results["has_required_fields"] = False
                validation_results["field_errors"].append(f"Missing {field}")
            elif lesson[field] is None:
                validation_results["field_errors"].append(f"{field} is None")
        
        # Structure scoring (0-100)
        score = 100
        score -= len(validation_results["field_errors"]) * 20
        validation_results["structure_score"] = max(0, score)
        
        return validation_results
    
    @staticmethod
    def validate_board_actions(board_actions: List[Dict]) -> Dict[str, Any]:
        """Validate board actions format and content."""
        if not isinstance(board_actions, list):
            return {
                "valid_format": False,
                "action_count": 0,
                "timing_errors": ["board_actions is not a list"],
                "visual_diversity_score": 0
            }
        
        timing_errors = []
        action_types = set()
        colors_used = set()
        
        for i, action in enumerate(board_actions):
            if not isinstance(action, dict):
                timing_errors.append(f"Action {i} is not a dict")
                continue
                
            # Check required fields
            if "type" not in action:
                timing_errors.append(f"Action {i} missing type")
            if "timestamp" not in action:
                timing_errors.append(f"Action {i} missing timestamp")
            
            # Track visual diversity
            if "type" in action:
                action_types.add(action["type"])
            if "fill" in action:
                colors_used.add(action["fill"])
            if "stroke" in action:
                colors_used.add(action["stroke"])
        
        # Visual diversity scoring
        diversity_score = (
            min(len(action_types) * 20, 60) +  # Type variety (max 60)
            min(len(colors_used) * 10, 40)     # Color variety (max 40)
        )
        
        return {
            "valid_format": True,
            "action_count": len(board_actions),
            "timing_errors": timing_errors,
            "visual_diversity_score": diversity_score,
            "action_types": list(action_types),
            "colors_used": list(colors_used)
        }
    
    @staticmethod
    def validate_narration_quality(narration: str) -> Dict[str, Any]:
        """Assess narration script quality."""
        if not isinstance(narration, str):
            return {
                "word_count": 0,
                "educational_quality_score": 0,
                "clarity_issues": ["narration is not a string"]
            }
        
        words = narration.split()
        word_count = len(words)
        
        # Educational quality indicators
        educational_keywords = [
            "learn", "understand", "concept", "example", "explain", "demonstrate",
            "shows", "means", "because", "therefore", "first", "next", "finally",
            "important", "key", "remember", "notice"
        ]
        
        clarity_issues = []
        educational_score = 0
        
        # Word count check
        if word_count < 20:
            clarity_issues.append("Narration too short")
        elif word_count > 500:
            clarity_issues.append("Narration too long")
        else:
            educational_score += 30
        
        # Educational language check
        educational_words_found = sum(
            1 for word in words 
            if any(keyword in word.lower() for keyword in educational_keywords)
        )
        educational_score += min(educational_words_found * 5, 40)
        
        # Sentence structure check
        sentences = narration.split('.')
        if len(sentences) >= 3:
            educational_score += 20
        
        # Technical content check (simple heuristic)
        if any(char.isupper() for char in narration) and any(char.isdigit() for char in narration):
            educational_score += 10
            
        return {
            "word_count": word_count,
            "educational_quality_score": min(educational_score, 100),
            "clarity_issues": clarity_issues,
            "sentence_count": len(sentences)
        }


class PerformanceMetrics:
    """Tracks system performance metrics."""
    
    def __init__(self):
        self.generation_times = []
        self.success_count = 0
        self.failure_count = 0
        self.validation_scores = []
        self.topic_performance = {}
    
    def record_generation(self, topic: str, success: bool, duration: float, validation_score: float):
        """Record a lesson generation attempt."""
        self.generation_times.append(duration)
        
        if success:
            self.success_count += 1
            self.validation_scores.append(validation_score)
        else:
            self.failure_count += 1
        
        if topic not in self.topic_performance:
            self.topic_performance[topic] = {"successes": 0, "failures": 0, "avg_score": 0}
        
        if success:
            self.topic_performance[topic]["successes"] += 1
            self.topic_performance[topic]["avg_score"] = statistics.mean([
                s for s in self.validation_scores if s > 0
            ]) if self.validation_scores else 0
        else:
            self.topic_performance[topic]["failures"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate performance summary statistics."""
        total_attempts = self.success_count + self.failure_count
        
        return {
            "total_lessons_generated": total_attempts,
            "success_rate": (self.success_count / total_attempts * 100) if total_attempts > 0 else 0,
            "average_generation_time": statistics.mean(self.generation_times) if self.generation_times else 0,
            "median_generation_time": statistics.median(self.generation_times) if self.generation_times else 0,
            "min_generation_time": min(self.generation_times) if self.generation_times else 0,
            "max_generation_time": max(self.generation_times) if self.generation_times else 0,
            "average_validation_score": statistics.mean(self.validation_scores) if self.validation_scores else 0,
            "validation_score_std": statistics.stdev(self.validation_scores) if len(self.validation_scores) > 1 else 0,
            "topic_performance": self.topic_performance
        }


async def generate_lesson_with_metrics(
    topic: str, 
    user_interest: str, 
    proficiency: str, 
    grade: str,
    validator: LessonValidator,
    metrics: PerformanceMetrics
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Generate a lesson and collect validation metrics."""
    
    start_time = time.time()
    
    try:
        # Generate lesson
        lesson = await generate_lesson(
            topic=topic,
            user_interest=user_interest, 
            proficiency_level=proficiency,
            grade_level=grade
        )
        
        generation_time = time.time() - start_time
        
        # Validate lesson
        validation_start = time.time()
        
        structure_validation = validator.validate_lesson_structure(lesson)
        board_validation = validator.validate_board_actions(lesson.get("board_actions", []))
        narration_validation = validator.validate_narration_quality(lesson.get("narration_script", ""))
        
        validation_time = time.time() - validation_start
        
        # Calculate overall validation score
        overall_score = (
            structure_validation["structure_score"] * 0.4 +
            board_validation["visual_diversity_score"] * 0.3 +
            narration_validation["educational_quality_score"] * 0.3
        )
        
        # Record metrics
        metrics.record_generation(topic, True, generation_time, overall_score)
        
        validation_results = {
            "success": True,
            "generation_time": generation_time,
            "validation_time": validation_time,
            "overall_score": overall_score,
            "structure": structure_validation,
            "board_actions": board_validation,
            "narration": narration_validation
        }
        
        return lesson, validation_results
        
    except Exception as e:
        generation_time = time.time() - start_time
        metrics.record_generation(topic, False, generation_time, 0)
        
        validation_results = {
            "success": False,
            "generation_time": generation_time,
            "error": str(e),
            "overall_score": 0
        }
        
        return {}, validation_results


async def run_comprehensive_evaluation():
    """Run the complete evaluation framework."""
    print("🚀 Starting Comprehensive Lesson Generation Evaluation")
    print("=" * 60)
    
    # Initialize components
    validator = LessonValidator()
    metrics = PerformanceMetrics()
    
    # Create results directory
    results_dir = Path("../evaluation_results/phase1")
    results_dir.mkdir(exist_ok=True, parents=True)
    
    # Flatten topics list
    all_topics = []
    for category, topics in STEM_TOPICS.items():
        all_topics.extend(topics)
    
    print(f"📚 Total topics: {len(all_topics)}")
    print(f"🎯 Target lessons: 100")
    
    # Generate lesson parameters (100 lessons across 20 topics = ~5 per topic)
    lesson_params = []
    lessons_per_topic = 100 // len(all_topics)
    extra_lessons = 100 % len(all_topics)
    
    for i, topic in enumerate(all_topics):
        topic_lesson_count = lessons_per_topic + (1 if i < extra_lessons else 0)
        
        for j in range(topic_lesson_count):
            lesson_params.append({
                "topic": topic,
                "user_interest": USER_INTERESTS[j % len(USER_INTERESTS)],
                "proficiency": PROFICIENCY_LEVELS[j % len(PROFICIENCY_LEVELS)],
                "grade": GRADE_LEVELS[j % len(GRADE_LEVELS)]
            })
    
    print(f"📝 Generated {len(lesson_params)} lesson parameters")
    
    # Generate lessons with progress tracking
    all_lessons = []
    all_validations = []
    
    for i, params in enumerate(lesson_params):
        print(f"\r⏳ Generating lesson {i+1}/100: {params['topic'][:30]}...", end="", flush=True)
        
        lesson, validation = await generate_lesson_with_metrics(
            topic=params["topic"],
            user_interest=params["user_interest"],
            proficiency=params["proficiency"], 
            grade=params["grade"],
            validator=validator,
            metrics=metrics
        )
        
        # Store results
        lesson_data = {
            "id": i + 1,
            "parameters": params,
            "lesson": lesson,
            "validation": validation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        all_lessons.append(lesson_data)
        all_validations.append(validation)
    
    print("\n✅ Lesson generation complete!")
    
    # Generate comprehensive report
    print("\n📊 Generating evaluation report...")
    
    performance_summary = metrics.get_summary()
    
    evaluation_report = {
        "evaluation_metadata": {
            "total_lessons": len(all_lessons),
            "topics_covered": len(all_topics),
            "evaluation_date": datetime.utcnow().isoformat(),
            "topic_categories": list(STEM_TOPICS.keys())
        },
        "performance_metrics": performance_summary,
        "detailed_results": all_lessons
    }
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Full detailed results
    with open(results_dir / f"full_evaluation_{timestamp}.json", "w") as f:
        json.dump(evaluation_report, f, indent=2)
    
    # Summary report for quick analysis
    summary_report = {
        "evaluation_metadata": evaluation_report["evaluation_metadata"],
        "performance_metrics": evaluation_report["performance_metrics"],
        "sample_lessons": all_lessons[:5]  # First 5 lessons as examples
    }
    
    with open(results_dir / f"summary_report_{timestamp}.json", "w") as f:
        json.dump(summary_report, f, indent=2)
    
    # Generate human-readable report
    generate_readable_report(performance_summary, all_validations, results_dir / f"report_{timestamp}.txt")
    
    print(f"\n📁 Results saved to: {results_dir}")
    print(f"   - Full data: full_evaluation_{timestamp}.json")
    print(f"   - Summary: summary_report_{timestamp}.json") 
    print(f"   - Report: report_{timestamp}.txt")
    
    return evaluation_report


def generate_readable_report(performance: Dict[str, Any], validations: List[Dict], output_path: Path):
    """Generate a human-readable evaluation report."""
    
    with open(output_path, "w") as f:
        f.write("LESSON GENERATION SYSTEM EVALUATION REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Lessons Generated: {performance['total_lessons_generated']}\n\n")
        
        f.write("PERFORMANCE METRICS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Success Rate: {performance['success_rate']:.1f}%\n")
        f.write(f"Average Generation Time: {performance['average_generation_time']:.2f} seconds\n")
        f.write(f"Median Generation Time: {performance['median_generation_time']:.2f} seconds\n")
        f.write(f"Generation Time Range: {performance['min_generation_time']:.2f}s - {performance['max_generation_time']:.2f}s\n")
        f.write(f"Average Validation Score: {performance['average_validation_score']:.1f}/100\n")
        f.write(f"Validation Score Std Dev: {performance['validation_score_std']:.1f}\n\n")
        
        f.write("TOPIC PERFORMANCE BREAKDOWN\n")
        f.write("-" * 30 + "\n")
        for topic, perf in performance['topic_performance'].items():
            f.write(f"{topic}: {perf['successes']} successes, {perf['failures']} failures, avg score: {perf['avg_score']:.1f}\n")
        
        f.write("\nVALIDATION ANALYSIS\n")
        f.write("-" * 20 + "\n")
        
        successful_validations = [v for v in validations if v.get("success", False)]
        if successful_validations:
            avg_overall = statistics.mean([v["overall_score"] for v in successful_validations])
            f.write(f"Average Overall Validation Score: {avg_overall:.1f}/100\n")
            
            # Structure scores
            structure_scores = [v["structure"]["structure_score"] for v in successful_validations if "structure" in v]
            if structure_scores:
                f.write(f"Average Structure Score: {statistics.mean(structure_scores):.1f}/100\n")
            
            # Visual diversity scores  
            visual_scores = [v["board_actions"]["visual_diversity_score"] for v in successful_validations if "board_actions" in v]
            if visual_scores:
                f.write(f"Average Visual Diversity Score: {statistics.mean(visual_scores):.1f}/100\n")
                
            # Educational quality scores
            edu_scores = [v["narration"]["educational_quality_score"] for v in successful_validations if "narration" in v]
            if edu_scores:
                f.write(f"Average Educational Quality Score: {statistics.mean(edu_scores):.1f}/100\n")


if __name__ == "__main__":
    print("Lesson Generation Evaluation Framework")
    print("Starting evaluation in 3 seconds...")
    
    async def main():
        try:
            report = await run_comprehensive_evaluation()
            print("\n🎉 Evaluation completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Evaluation failed: {e}")
            raise
    
    asyncio.run(main())