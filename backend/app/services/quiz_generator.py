"""Quiz generator service using Groq LLM."""
import json
import re
from typing import Dict, Any
from datetime import datetime

from app.core.config import get_settings
from langchain_groq import ChatGroq

settings = get_settings()


def _clean_json_response(content: str) -> str:
    """Clean and extract JSON from LLM response."""
    # Remove markdown code blocks if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    # Fix common JSON issues
    content = content.replace(""", '"').replace(""", '"')  # Fix curly quotes
    content = re.sub(r',\s*([}\]])', r'\1', content)  # Remove trailing commas
    
    return content


def _validate_quiz_data(data: Dict[str, Any]) -> bool:
    """Validate quiz data structure."""
    if not data or "questions" not in data:
        return False
    
    if not isinstance(data["questions"], list):
        return False
    
    for q in data["questions"]:
        # Check required fields
        if not all(k in q for k in ["id", "question", "options", "correctAnswer", "explanation"]):
            return False
        
        # Check options count
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            return False
        
        # Check correct answer is valid index
        if not isinstance(q["correctAnswer"], int) or q["correctAnswer"] not in [0, 1, 2, 3]:
            return False
        
        # Check explanation structure
        if not isinstance(q["explanation"], dict):
            return False
        if "correct" not in q["explanation"] or "incorrect" not in q["explanation"]:
            return False
        if not isinstance(q["explanation"]["incorrect"], dict):
            return False
    
    return True


def _format_explanations(quiz_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all explanations are properly formatted."""
    formatted_questions = []
    
    for q in quiz_data["questions"]:
        # Ensure incorrect explanations exist for all options
        incorrect_explanations = {}
        for i in range(4):
            if i == q["correctAnswer"]:
                incorrect_explanations[str(i)] = q["explanation"]["correct"]
            else:
                # Try to get existing explanation or create default
                incorrect_explanations[str(i)] = q["explanation"]["incorrect"].get(
                    str(i),
                    f"This option is incorrect. {q['explanation']['correct']}"
                )
        
        formatted_question = {
            **q,
            "explanation": {
                "correct": q["explanation"]["correct"],
                "incorrect": incorrect_explanations
            }
        }
        formatted_questions.append(formatted_question)
    
    return {
        **quiz_data,
        "questions": formatted_questions
    }


async def generate_quiz(
    topic: str,
    topic_description: str,
    num_questions: int = 8
) -> Dict[str, Any]:
    """
    Generate a quiz using Groq LLM.
    
    Args:
        topic: Main topic of the quiz
        topic_description: Detailed description of the topic
        num_questions: Number of questions to generate (default: 8)
    
    Returns:
        Dictionary containing quiz data with questions and metadata
    
    Raises:
        ValueError: If required fields are missing or API key not set
        Exception: If quiz generation fails
    """
    if not topic or not topic_description:
        raise ValueError("Topic and topic_description are required")
    
    groq_key = settings.groq_api_key
    if not groq_key:
        raise ValueError("GROQ_API_KEY not configured")
    
    # Build the prompt
    prompt = f"""Generate a JSON object for a balanced multiple-choice quiz based on the given input.

Inputs:
- Topic: {topic}
- Topic Description: {topic_description}

Quiz Structure:
- The quiz should contain {num_questions} questions, distributed as follows:
  - 3 Easy: Basic recall-based questions
  - 3 Medium: Questions requiring understanding and application
  - 2 Hard: Analytical, multi-step, or problem-solving questions
- The order of questions must be: Easy → Medium → Hard.

Output Format:
{{
  "questions": [
    {{
      "id": "1",
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctAnswer": 0,
      "difficulty": "easy",
      "explanation": {{
        "correct": "Explanation (50-100 words) why the correct answer is right, including relevant concepts and principles",
        "incorrect": {{
          "0": "Brief explanation why Option A is incorrect (if not the correct answer)",
          "1": "Brief explanation why Option B is incorrect (if not the correct answer)",
          "2": "Brief explanation why Option C is incorrect (if not the correct answer)",
          "3": "Brief explanation why Option D is incorrect (if not the correct answer)"
        }}
      }}
    }}
  ]
}}

Requirements:
1. Each question MUST include detailed explanations for both correct and incorrect answers
2. The correct answer explanation should be comprehensive and educational
3. Each incorrect answer explanation should clearly explain why that option is wrong
4. Use factual, clear language in explanations
5. Include relevant terminology and concepts in explanations

Question Generation Rules:
- Each question must have exactly 4 options
- Options should be clear and concise (max 30 characters)
- Progress from Easy to Hard difficulty
- Include comprehensive explanations for ALL answers
- Correct answer should be a number between 0 and 3 only (Important)

Format all explanations in clear, educational language. Do not use placeholders.
Return only a valid JSON object with no additional text."""
    
    try:
        print(f"[QuizGen] Generating quiz for topic: {topic}")
        
        # Initialize Groq LLM
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=groq_key,
            max_tokens=8000
        )
        
        # Invoke LLM
        response = await llm.ainvoke(prompt)
        
        # Extract content
        if hasattr(response, "content"):
            content = response.content
        else:
            content = str(response)
        
        print(f"[QuizGen] Received response, length: {len(content)}")
        
        # Clean and parse JSON
        cleaned_content = _clean_json_response(content)
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', cleaned_content)
        if json_match:
            cleaned_content = json_match.group(0)
        
        quiz_data = json.loads(cleaned_content)
        
        # Validate structure
        if not _validate_quiz_data(quiz_data):
            raise ValueError("Invalid quiz data structure received from LLM")
        
        # Format explanations
        formatted_quiz = _format_explanations(quiz_data)
        
        # Add metadata
        enriched_quiz = {
            **formatted_quiz,
            "metadata": {
                "topic": topic,
                "topic_description": topic_description,
                "generated_at": datetime.utcnow(),
                "question_count": len(formatted_quiz["questions"])
            }
        }
        
        print(f"[QuizGen] Successfully generated quiz with {len(formatted_quiz['questions'])} questions")
        
        return enriched_quiz
    
    except json.JSONDecodeError as e:
        print(f"[QuizGen] JSON parsing error: {e}")
        print(f"[QuizGen] Content: {content[:500]}...")
        raise Exception(f"Failed to parse quiz response: {str(e)}")
    
    except Exception as e:
        print(f"[QuizGen] Error generating quiz: {e}")
        raise Exception(f"Quiz generation failed: {str(e)}")
