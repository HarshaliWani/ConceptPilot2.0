#!/usr/bin/env python3
"""
Phase 2: Pedagogical Evaluation Runner
======================================

LLM-as-Judge + Manual Review System
Research validation without human studies - automated content quality assessment.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from pedagogical_evaluation import run_pedagogical_evaluation


def main():
    """Main entry point for Phase 2 evaluation."""
    print("🎓 PHASE 2: PEDAGOGICAL EVALUATION")
    print("=" * 40)
    print("📋 Evaluation Overview:")
    print("   • LLM-as-Judge quiz evaluation (20 quizzes)")
    print("   • LLM-as-Judge flashcard evaluation (10 sets)")
    print("   • Manual review framework (10 items)")
    print("   • Rubric-based scoring (1-5 scale)")
    print("   • Research-ready pedagogical metrics")
    print()
    
    try:
        # Get evaluation parameters
        print("⚙️ Configuration Options:")
        print("   Default: 20 quizzes, 10 flashcard sets, 10 manual review items")
        
        use_defaults = input("🚀 Use default settings? (Y/n): ").strip().lower()
        
        if use_defaults in ['n', 'no']:
            try:
                num_quizzes = int(input("   Number of quizzes to evaluate (1-50): ") or 20)
                num_flashcard_sets = int(input("   Number of flashcard sets (1-20): ") or 10)
                manual_review_count = int(input("   Manual review items (1-20): ") or 10)
                
                # Validate ranges
                num_quizzes = max(1, min(50, num_quizzes))
                num_flashcard_sets = max(1, min(20, num_flashcard_sets))
                manual_review_count = max(1, min(20, manual_review_count))
                
            except ValueError:
                print("⚠️ Invalid input, using defaults...")
                num_quizzes = 20
                num_flashcard_sets = 10
                manual_review_count = 10
        else:
            num_quizzes = 20
            num_flashcard_sets = 10
            manual_review_count = 10
        
        print()
        print(f"📊 Final Configuration:")
        print(f"   • Quizzes: {num_quizzes}")
        print(f"   • Flashcard Sets: {num_flashcard_sets}")
        print(f"   • Manual Review Items: {manual_review_count}")
        print(f"   • Estimated Time: {(num_quizzes + num_flashcard_sets) * 2 + manual_review_count * 6} minutes")
        print()
        
        confirm = input("🚀 Start pedagogical evaluation? (Y/n): ").strip().lower()
        if confirm in ['n', 'no']:
            print("Evaluation cancelled.")
            return 0
        
    except KeyboardInterrupt:
        print("\nEvaluation cancelled.")
        return 0
    
    print("\n⏳ Starting pedagogical evaluation...")
    
    try:
        # Run the async evaluation
        results = asyncio.run(run_pedagogical_evaluation(
            num_quizzes=num_quizzes,
            num_flashcard_sets=num_flashcard_sets,
            manual_review_count=manual_review_count
        ))
        
        print("\n" + "=" * 50)
        print("✅ PEDAGOGICAL EVALUATION COMPLETED!")
        print("=" * 50)
        
        # Show key results
        metadata = results['evaluation_metadata']
        print(f"📊 Key Results:")
        print(f"   • Quizzes Evaluated: {metadata['num_quizzes_evaluated']}")
        print(f"   • Flashcard Sets Evaluated: {metadata['num_flashcard_sets_evaluated']}")
        print(f"   • Manual Review Items: {metadata['num_manual_review_items']}")
        print(f"   • LLM Judge Model: {metadata['llm_judge_model']}")
        
        # Quick quality summary
        quiz_evals = results['quiz_evaluations']
        successful_quiz_evals = [q for q in quiz_evals if "error" not in q.get("llm_evaluation", {})]
        
        if successful_quiz_evals:
            overall_scores = []
            for eval_data in successful_quiz_evals:
                llm_eval = eval_data["llm_evaluation"]
                if "overall_score" in llm_eval:
                    overall_scores.append(float(llm_eval["overall_score"]))
            
            if overall_scores:
                import statistics
                print(f"   • Quiz Quality Score: {statistics.mean(overall_scores):.1f}/5.0")
        
        flashcard_evals = results['flashcard_evaluations']
        successful_flashcard_evals = [f for f in flashcard_evals if "error" not in f.get("llm_evaluation", {})]
        
        if successful_flashcard_evals:
            overall_scores = []
            for eval_data in successful_flashcard_evals:
                llm_eval = eval_data["llm_evaluation"]
                if "overall_score" in llm_eval:
                    overall_scores.append(float(llm_eval["overall_score"]))
            
            if overall_scores:
                import statistics
                print(f"   • Flashcard Quality Score: {statistics.mean(overall_scores):.1f}/5.0")
        
        print(f"\n📁 Results saved in: pedagogical_evaluation_results/")
        print(f"   • Full evaluation data for research analysis")
        print(f"   • Manual review templates ready for scoring")
        print(f"   • Rubric-based assessment framework")
        
        print(f"\n📝 Next Steps:")
        print(f"   1. Review LLM judge evaluations in JSON files")
        print(f"   2. Complete manual review using provided templates")
        print(f"   3. Analyze rubric scores for research insights")
        print(f"   4. Use data for publication quality validation")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Evaluation interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Evaluation failed with error:")
        print(f"   {type(e).__name__}: {e}")
        print(f"\n💡 Troubleshooting:")
        print(f"   • Check if Phase 1 evaluation completed successfully")
        print(f"   • Verify LLM API keys are configured (GROQ)")
        print(f"   • Ensure quiz/flashcard generators are working")
        print(f"   • Check system resources and network connectivity")
        
        return 1
    
    return 0


def run_quick_test():
    """Run a quick test with minimal items."""
    print("🧪 QUICK PEDAGOGICAL TEST")
    print("=" * 30)
    print("Testing with 2 quizzes, 2 flashcard sets, 2 manual review items")
    print()
    
    try:
        results = asyncio.run(run_pedagogical_evaluation(
            num_quizzes=2,
            num_flashcard_sets=2,
            manual_review_count=2
        ))
        print("✅ Quick test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        exit_code = run_quick_test()
    else:
        exit_code = main()
    
    sys.exit(exit_code)