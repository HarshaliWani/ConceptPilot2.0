"""
Manual Review Template Generator & Analyzer
==========================================

Tools for conducting manual pedagogical evaluation and analyzing results.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class ManualReviewAnalyzer:
    """Analyze completed manual review results and generate insights."""
    
    def analyze_completed_reviews(self, review_file_path: Path) -> Dict[str, Any]:
        """Analyze a completed manual review file."""
        
        try:
            with open(review_file_path, 'r') as f:
                review_data = json.load(f)
        except Exception as e:
            return {"error": f"Failed to load review file: {e}"}
        
        analysis = {
            "analysis_metadata": {
                "review_file": str(review_file_path),
                "analysis_date": datetime.utcnow().isoformat(),
                "content_type": review_data.get("review_metadata", {}).get("content_type", "unknown")
            },
            "completion_stats": {},
            "score_analysis": {},
            "reliability_metrics": {},
            "insights": []
        }
        
        items = review_data.get("items_for_review", [])
        completed_items = []
        
        # Check completion status
        for item in items:
            scores = item.get("manual_scores", {})
            overall = item.get("overall_assessment", {})
            
            # Count completed dimensions
            completed_dimensions = sum(1 for dim_data in scores.values() 
                                    if dim_data.get("score") is not None)
            
            has_overall_score = overall.get("overall_score") is not None
            
            if completed_dimensions > 0 or has_overall_score:
                completed_items.append(item)
        
        analysis["completion_stats"] = {
            "total_items": len(items),
            "completed_items": len(completed_items),
            "completion_rate": len(completed_items) / len(items) * 100 if items else 0
        }
        
        if not completed_items:
            analysis["insights"].append("No completed reviews found - manual review needed")
            return analysis
        
        # Analyze scores by rubric dimension
        rubric_dimensions = set()
        for item in completed_items:
            rubric_dimensions.update(item.get("manual_scores", {}).keys())
        
        dimension_scores = {}
        overall_scores = []
        confidence_scores = []
        review_times = []
        
        for item in completed_items:
            # Overall scores
            overall_score = item.get("overall_assessment", {}).get("overall_score")
            if overall_score is not None:
                overall_scores.append(overall_score)
            
            # Review time
            review_time = item.get("overall_assessment", {}).get("time_spent_minutes")
            if review_time is not None:
                review_times.append(review_time)
            
            # Dimension scores
            for dim in rubric_dimensions:
                if dim in item.get("manual_scores", {}):
                    dim_data = item["manual_scores"][dim]
                    score = dim_data.get("score")
                    confidence = dim_data.get("confidence")
                    
                    if score is not None:
                        if dim not in dimension_scores:
                            dimension_scores[dim] = []
                        dimension_scores[dim].append(score)
                    
                    if confidence is not None:
                        confidence_scores.append(confidence)
        
        # Calculate statistics
        import statistics
        
        if overall_scores:
            analysis["score_analysis"]["overall"] = {
                "mean": statistics.mean(overall_scores),
                "median": statistics.median(overall_scores),
                "std_dev": statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0,
                "min": min(overall_scores),
                "max": max(overall_scores),
                "distribution": {i: overall_scores.count(i) for i in range(1, 6)}
            }
        
        analysis["score_analysis"]["dimensions"] = {}
        for dim, scores in dimension_scores.items():
            if scores:
                analysis["score_analysis"]["dimensions"][dim] = {
                    "mean": statistics.mean(scores),
                    "median": statistics.median(scores),
                    "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                    "count": len(scores)
                }
        
        if confidence_scores:
            analysis["reliability_metrics"]["confidence"] = {
                "mean": statistics.mean(confidence_scores),
                "median": statistics.median(confidence_scores),
                "low_confidence_count": sum(1 for c in confidence_scores if c <= 2)
            }
        
        if review_times:
            analysis["reliability_metrics"]["review_time"] = {
                "mean_minutes": statistics.mean(review_times),
                "median_minutes": statistics.median(review_times),
                "total_hours": sum(review_times) / 60
            }
        
        # Generate insights
        if overall_scores:
            avg_score = statistics.mean(overall_scores)
            if avg_score >= 4.0:
                analysis["insights"].append("High quality content - scores consistently above 4.0")
            elif avg_score >= 3.0:
                analysis["insights"].append("Good quality content - scores in acceptable range")
            else:
                analysis["insights"].append("Quality concerns - scores below 3.0 indicate issues")
        
        # Check dimension score consistency
        if len(dimension_scores) >= 2:
            dim_means = [statistics.mean(scores) for scores in dimension_scores.values()]
            if max(dim_means) - min(dim_means) > 1.0:
                analysis["insights"].append("Inconsistent quality across dimensions - some areas need improvement")
        
        return analysis
    
    def generate_manual_review_report(self, analysis: Dict[str, Any], output_path: Path):
        """Generate a human-readable manual review report."""
        
        with open(output_path, 'w') as f:
            f.write("MANUAL REVIEW ANALYSIS REPORT\n")
            f.write("=" * 35 + "\n\n")
            
            metadata = analysis["analysis_metadata"]
            f.write(f"Analysis Date: {datetime.fromisoformat(metadata['analysis_date']).strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Content Type: {metadata['content_type'].title()}\n")
            f.write(f"Review File: {metadata['review_file']}\n\n")
            
            # Completion statistics
            f.write("COMPLETION STATISTICS\n")
            f.write("-" * 20 + "\n")
            
            completion = analysis["completion_stats"]
            f.write(f"Total Items: {completion['total_items']}\n")
            f.write(f"Completed Items: {completion['completed_items']}\n") 
            f.write(f"Completion Rate: {completion['completion_rate']:.1f}%\n\n")
            
            # Score analysis
            if "overall" in analysis["score_analysis"]:
                f.write("OVERALL SCORE ANALYSIS\n")
                f.write("-" * 22 + "\n")
                
                overall = analysis["score_analysis"]["overall"]
                f.write(f"Mean Score: {overall['mean']:.2f}/5.0\n")
                f.write(f"Median Score: {overall['median']:.1f}/5.0\n")
                f.write(f"Standard Deviation: {overall['std_dev']:.2f}\n")
                f.write(f"Score Range: {overall['min']}-{overall['max']}\n")
                
                f.write(f"\nScore Distribution:\n")
                for score, count in overall['distribution'].items():
                    f.write(f"  {score}/5: {count} items\n")
                f.write("\n")
            
            # Dimension analysis
            if analysis["score_analysis"]["dimensions"]:
                f.write("RUBRIC DIMENSION ANALYSIS\n")
                f.write("-" * 25 + "\n")
                
                for dim, stats in analysis["score_analysis"]["dimensions"].items():
                    f.write(f"{dim.replace('_', ' ').title()}: {stats['mean']:.2f}/5.0 ")
                    f.write(f"(σ={stats['std_dev']:.2f}, n={stats['count']})\n")
                f.write("\n")
            
            # Reliability metrics
            if analysis["reliability_metrics"]:
                f.write("RELIABILITY METRICS\n")
                f.write("-" * 18 + "\n")
                
                if "confidence" in analysis["reliability_metrics"]:
                    conf = analysis["reliability_metrics"]["confidence"]
                    f.write(f"Mean Reviewer Confidence: {conf['mean']:.2f}/5.0\n")
                    f.write(f"Low Confidence Reviews: {conf['low_confidence_count']}\n")
                
                if "review_time" in analysis["reliability_metrics"]:
                    time_stats = analysis["reliability_metrics"]["review_time"]
                    f.write(f"Mean Review Time: {time_stats['mean_minutes']:.1f} minutes\n")
                    f.write(f"Total Review Time: {time_stats['total_hours']:.1f} hours\n")
                
                f.write("\n")
            
            # Key insights
            f.write("KEY INSIGHTS\n")
            f.write("-" * 12 + "\n")
            
            for i, insight in enumerate(analysis["insights"], 1):
                f.write(f"{i}. {insight}\n")
            
            if not analysis["insights"]:
                f.write("No specific insights generated - review completion needed\n")


def create_empty_manual_review_template(content_type: str, topics: List[str], output_dir: Path):
    """Create an empty manual review template for specified topics."""
    
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create sample items based on content type
    sample_items = []
    
    for i, topic in enumerate(topics[:10]):  # Limit to 10 items
        if content_type == "quiz":
            sample_items.append({
                "quiz_id": i + 1,
                "generation_params": {
                    "topic": topic,
                    "user_interest": "technology",
                    "proficiency_level": "intermediate",
                    "grade_level": "high school"
                },
                "quiz_data": {
                    "topic": topic,
                    "questions": [{
                        "id": 1,
                        "question": f"Sample question about {topic}",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correctAnswer": 0,
                        "explanation": "Sample explanation"
                    }]
                }
            })
        else:  # flashcard
            sample_items.append({
                "flashcard_set_id": i + 1,
                "generation_params": {
                    "topic": topic,
                    "user_interest": "science",
                    "proficiency_level": "beginner",
                    "grade_level": "middle school"
                },
                "flashcard_data": {
                    "topic": topic,
                    "flashcards": [
                        {"front": f"What is {topic}?", "back": f"Sample definition of {topic}"},
                        {"front": f"Key application of {topic}", "back": "Sample application"}
                    ]
                }
            })
    
    # Create manual review interface
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
    from pedagogical_evaluation import ManualReviewInterface
    reviewer = ManualReviewInterface()
    
    template = reviewer.generate_review_template(content_type, sample_items)
    
    # Save template
    filename = f"manual_review_{content_type}_template_{timestamp}.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ Created manual review template: {filepath}")
    print(f"   Content Type: {content_type.title()}")
    print(f"   Items: {len(sample_items)}")
    print(f"   Estimated Time: {len(sample_items) * 6} minutes")
    
    return filepath


if __name__ == "__main__":
    print("Manual Review Tools")
    print("=" * 20)
    
    # Example: Create templates for manual review
    topics = [
        "Quadratic Equations", "Newton's Laws", "Ohm's Law",
        "Calculus Derivatives", "Wave Properties", "Digital Logic"
    ]
    
    results_dir = Path("manual_review_templates")
    
    print("Creating sample manual review templates...")
    
    # Create quiz template
    quiz_template = create_empty_manual_review_template("quiz", topics, results_dir)
    
    # Create flashcard template  
    flashcard_template = create_empty_manual_review_template("flashcard", topics, results_dir)
    
    print(f"\n📁 Templates created in: {results_dir}")
    print(f"\n📝 Instructions:")
    print(f"   1. Open the JSON template files")
    print(f"   2. Fill in scores (1-5) for each rubric dimension")
    print(f"   3. Add reviewer comments and confidence ratings")
    print(f"   4. Save completed templates")
    print(f"   5. Run analysis script on completed files")