# 📊 Research Evaluation System

> Comprehensive automated evaluation framework for lesson generation system validation

## 🎯 Purpose

This evaluation system generates **100 lessons across 20 STEM topics** and performs automated validation with technical metrics for research paper analysis. No students required - fully automated system validation.

## 📋 What It Does

### ✅ Core Evaluation Tasks
- **Generate 100 lessons** on Math, Physics, and Circuit topics
- **Automated quality validation** of all outputs  
- **Technical metrics collection** (success rates, latency, scores)
- **Research-ready data output** in JSON and text formats

### 📚 Topics Covered (20 STEM Topics)

**Mathematics (7 topics):**
- Quadratic Equations
- Calculus Derivatives
- Probability Theory
- Linear Algebra
- Trigonometry
- Statistics and Data Analysis
- Geometry Proofs

**Physics (7 topics):**
- Newton's Laws of Motion
- Electromagnetic Induction
- Wave Properties and Interference
- Thermodynamics First Law
- Quantum Mechanics Basics
- Optics and Refraction
- Energy Conservation

**Circuits (6 topics):**
- Ohm's Law Applications
- AC vs DC Current
- Capacitors and Inductors
- Digital Logic Gates
- Transistor Operation
- Circuit Analysis Methods

### 🔍 Validation Metrics

**Structure Validation (40% weight):**
- Required field presence
- Data type correctness
- Schema compliance

**Visual Board Actions (30% weight):**
- Action format validation
- Visual diversity scoring
- Timing precision
- Konva.js compatibility

**Educational Quality (30% weight):**
- Narration script assessment
- Educational language usage
- Content clarity metrics
- Teaching effectiveness indicators

## 🚀 Quick Start

### Option 1: Windows Batch File (Easiest)
```batch
# Simply double-click or run:
run_research_evaluation.bat
```

### Option 2: Direct Python Execution
```bash
# Activate virtual environment (if using one)
.venv\Scripts\activate

# Run full evaluation (100 lessons)
python run_evaluation.py

# Or test with a smaller batch first
python validate_lessons.py mini 5
```

### Option 3: Test Single Lesson
```bash
# Test one lesson generation
python validate_lessons.py single "Quadratic Equations"

# Test with custom topic
python validate_lessons.py single "Newton's Laws of Motion"
```

## 📁 Output Files

After completion, find results in `evaluation_results/` directory:

### 📊 Main Research Files
- **`full_evaluation_YYYYMMDD_HHMMSS.json`** - Complete dataset with all 100 lessons
- **`summary_report_YYYYMMDD_HHMMSS.json`** - Key metrics + sample lessons
- **`report_YYYYMMDD_HHMMSS.txt`** - Human-readable analysis report

### 📈 Key Metrics Included
- **Success Rate** - Percentage of successful lesson generations
- **Average Generation Time** - Mean time per lesson (seconds)
- **Quality Scores** - Validation scores (0-100 scale)
- **Topic Performance** - Per-topic success/failure breakdown
- **Technical Statistics** - Latency distributions, error rates

## 🔧 System Requirements

### Prerequisites
- Python 3.8+ with async support
- Required packages: `langchain-groq`, `langchain-core`
- API access: GROQ or OpenAI (configured in environment)
- Backend dependencies installed (`pip install -r requirements.txt`)

### Optional
- MongoDB (for full system testing)
- TTS service (for audio generation testing)

## 🧪 Testing & Debugging

### Quick System Check
```bash
# Test single lesson (fastest validation)
python validate_lessons.py single
```

### Mini Evaluation (5 lessons)
```bash
# Small batch for debugging
python validate_lessons.py mini 5
```

### Full Research Evaluation (100 lessons)
```bash
# Complete research dataset
python run_evaluation.py
```

## 📖 Understanding the Results

### Success Rate Interpretation
- **90-100%**: Excellent system reliability
- **80-89%**: Good performance, minor issues
- **70-79%**: Acceptable, needs optimization 
- **<70%**: Requires investigation

### Quality Score Breakdown
- **90-100**: Exceptional lesson quality
- **80-89**: High quality, publication ready
- **70-79**: Good quality, minor improvements needed
- **60-69**: Acceptable quality
- **<60**: Needs significant improvement

### Latency Expectations
- **Target**: <5 seconds per lesson
- **Acceptable**: 5-15 seconds
- **Concerning**: >15 seconds

## 🔬 Research Applications

### For Publications
- Use success rates to demonstrate system reliability
- Quality scores show educational content effectiveness
- Latency metrics prove real-time feasibility
- Topic diversity shows generalization capability

### Comparative Analysis
- Run evaluations before/after system improvements
- Compare different AI models (GROQ vs OpenAI)
- Analyze performance across topic categories
- Study correlation between complexity and quality

## 🛠 Troubleshooting

### Common Issues

**"No API keys found"**
- Check GROQ_API_KEY environment variable
- Verify API key validity and permissions

**"Module not found errors"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**"Low success rates"**
- Check API rate limits
- Verify internet connectivity
- Review error messages in detailed results

**"Slow generation times"**
- Check API latency
- Monitor system resources
- Consider running smaller batches

### Debug Mode
Add verbose logging by modifying the evaluation script:
```python
# In evaluation_framework.py, line ~25
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Sample Results

```
🔬 EVALUATION COMPLETED SUCCESSFULLY!
📊 Key Results:
   • Total Lessons: 100
   • Success Rate: 94.0%
   • Avg Generation Time: 3.2s
   • Avg Quality Score: 85.7/100
   
   📁 Results saved in: evaluation_results/
```

## 🤝 Research Collaboration

The evaluation framework is designed for:
- **Reproducible results** - Same topics, deterministic validation
- **Scalable analysis** - Easy to extend to more topics/lessons
- **Data transparency** - Full JSON outputs for independent analysis
- **Metric standardization** - Consistent scoring across evaluations

---

**💡 Need Help?** 
- Check the troubleshooting section above
- Review error messages in console output
- Examine detailed JSON results for debugging
- Test with single lessons first (`validate_lessons.py single`)