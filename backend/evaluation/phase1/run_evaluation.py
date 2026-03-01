#!/usr/bin/env python3
"""
Research Evaluation Runner
=========================

Quick script to run the comprehensive lesson generation evaluation
for research paper validation.

Usage:
    python run_evaluation.py

Output:
    - Generates 100 lessons across 20 STEM topics
    - Creates detailed validation metrics
    - Saves results in evaluation_results/ directory
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from evaluation_framework import run_comprehensive_evaluation


def main():
    """Main entry point for evaluation."""
    print("🔬 LESSON GENERATION RESEARCH EVALUATION")
    print("=" * 50)
    print("📋 Evaluation Plan:")
    print("   • Generate 100 lessons across 20 STEM topics")
    print("   • Topics: Math, Physics, Circuits")
    print("   • Automated validation & quality metrics")
    print("   • Performance measurements")
    print("   • Research-ready data output")
    print()
    
    # Confirm execution
    try:
        response = input("🚀 Start evaluation? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Evaluation cancelled.")
            return
    except KeyboardInterrupt:
        print("\nEvaluation cancelled.")
        return
    
    print("\n⏳ Starting evaluation...")
    
    try:
        # Run the async evaluation
        report = asyncio.run(run_comprehensive_evaluation())
        
        print("\n" + "=" * 50)
        print("✅ EVALUATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        # Show key metrics
        metrics = report['performance_metrics']
        print(f"📊 Key Results:")
        print(f"   • Total Lessons: {metrics['total_lessons_generated']}")
        print(f"   • Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   • Avg Generation Time: {metrics['average_generation_time']:.2f}s")
        print(f"   • Avg Quality Score: {metrics['average_validation_score']:.1f}/100")
        
        print(f"\n📁 Results saved in: evaluation_results/")
        print(f"   Use the JSON files for detailed research analysis")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Evaluation interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed with error:")
        print(f"   {type(e).__name__}: {e}")
        print(f"\n💡 Troubleshooting tips:")
        print(f"   • Check if backend dependencies are installed")
        print(f"   • Ensure MongoDB is running (if required)")
        print(f"   • Verify API keys are configured")
        
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)