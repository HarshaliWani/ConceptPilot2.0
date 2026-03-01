# 🔬 Evaluation System Documentation

## 📁 Organized Structure

```
backend/
├── evaluation/                              # All evaluation scripts and docs
│   ├── COMPLETE_RESEARCH_EVALUATION_GUIDE.md    # Main documentation
│   ├── phase1/                              # Technical System Validation
│   │   ├── evaluation_framework.py         # Core evaluation logic
│   │   ├── run_evaluation.py                # Python runner
│   │   ├── validate_lessons.py             # Single lesson testing
│   │   ├── run_research_evaluation.bat     # Windows batch runner
│   │   ├── Run-ResearchEvaluation.ps1      # PowerShell runner  
│   │   └── RESEARCH_EVALUATION_README.md   # Phase 1 documentation
│   └── phase2/                              # Pedagogical Quality Assessment
│       ├── pedagogical_evaluation.py       # LLM-as-judge framework
│       ├── run_phase2_evaluation.py        # Python runner
│       ├── manual_review_tools.py          # Manual review utilities
│       ├── run_phase2_evaluation.bat       # Windows batch runner
│       └── PHASE2_PEDAGOGICAL_EVALUATION.md # Phase 2 documentation
├── evaluation_results/                      # All results consolidated here
│   ├── phase1/                              # Technical validation results 
│   │   ├── full_evaluation_*.json          # Complete lesson dataset
│   │   ├── summary_report_*.json           # Key metrics summary
│   │   ├── report_*.txt                     # Human-readable report
│   │   └── test_lesson_*.json               # Individual test results
│   └── phase2/                              # Pedagogical assessment results
│       ├── pedagogical_evaluation_*.json   # LLM judge evaluations
│       ├── manual_review_*_template_*.json  # Manual scoring templates
│       └── pedagogical_summary_*.txt       # Analysis reports
└── run_evaluation.bat                       # Main evaluation launcher
```

## 🚀 Quick Start

### **Option 1: Main Launcher (Recommended)**
```batch
# Double-click or run from backend directory:
run_evaluation.bat

# Choose your option:
# 1. Phase 1 only (100 lessons, technical metrics)
# 2. Phase 2 only (pedagogical quality assessment) 
# 3. Complete evaluation (both phases)
# 4. Quick test (small samples)
# 5. View results
```

### **Option 2: Individual Phases**
```bash
# Phase 1: Technical Validation
cd evaluation/phase1
run_research_evaluation.bat

# Phase 2: Pedagogical Assessment  
cd evaluation/phase2
run_phase2_evaluation.bat
```

### **Option 3: Python Direct**
```python
# Phase 1
cd evaluation/phase1
python run_evaluation.py

# Phase 2  
cd evaluation/phase2
python run_phase2_evaluation.py
```

## 📊 What Each Phase Delivers

### **Phase 1: Technical System Validation**
- **100 lessons** generated across 20 STEM topics
- **Success rate** and **reliability metrics** 
- **Generation latency** and **scalability** data
- **Quality scores** using automated validation
- **Results**: `evaluation_results/phase1/`

### **Phase 2: Pedagogical Quality Assessment**
- **LLM-as-Judge evaluation** using educational rubrics
- **Manual review framework** for expert validation
- **Quiz and flashcard quality** assessment (1-5 scales)
- **Statistical analysis** with reliability metrics
- **Results**: `evaluation_results/phase2/`

## 🎯 Research Usage

### **For Academic Publications**
1. **Run both phases** for complete validation
2. **Use statistics** from results JSON files
3. **Reference methodology** in documentation
4. **Include reliability metrics** for credibility

### **For System Development** 
1. **Monitor quality scores** for improvements
2. **Use automated evaluation** for continuous testing
3. **Apply manual review** for quality assurance
4. **Track performance** over iterations

## 📈 Expected Results

### **Phase 1 Benchmarks**
- **Success Rate**: 95-100% (system reliability)
- **Quality Score**: 85-95/100 (content validation) 
- **Generation Time**: <30s per lesson (efficiency)

### **Phase 2 Benchmarks**  
- **Quiz Quality**: 4.0-4.5/5.0 (educational standard)
- **Flashcard Quality**: 3.8-4.3/5.0 (learning effectiveness)
- **LLM-Manual Correlation**: 0.6-0.8 (automation reliability)

## 🛠️ Troubleshooting

### **Common Issues**
- **Import errors**: Ensure you're in the right directory and virtual environment is activated
- **Path errors**: Use the batch files which handle paths automatically
- **API errors**: Check GROQ_API_KEY environment variable

### **Quick Tests**
```bash
# Test Phase 1 (5 lessons)
cd evaluation/phase1 
python validate_lessons.py mini 5

# Test Phase 2 (2 items)
cd evaluation/phase2
python run_phase2_evaluation.py test
```

### **Results Location**
All results are automatically saved to:
- **`evaluation_results/phase1/`** - Technical validation data
- **`evaluation_results/phase2/`** - Pedagogical assessment data

---

**📧 Need Help?** Check the detailed documentation in each phase folder or run the quick tests to validate your setup.