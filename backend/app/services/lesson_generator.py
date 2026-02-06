"""Lesson generator service (wrapper around LangChain)."""
import json
from typing import Dict, Any
from datetime import datetime

from app.core.config import get_settings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

settings = get_settings()


def _build_mock_lesson(topic: str, user_interest: str, source: str) -> Dict[str, Any]:
    """Create a deterministic mock lesson for fallback scenarios."""
    now = datetime.utcnow().isoformat()
    return {
        "topic": topic,
        "title": f"Intro to {topic}",
        "narration_script": (
            f"A short narration about {topic} using examples from {user_interest}."
        ),
        "board_actions": [
            {
                "timestamp": 0,
                "type": "text",
                "content": topic,
                "x": 50,
                "y": 20,
                "fontSize": 24,
                "fill": "black",
            },
            {
                "timestamp": 3,
                "type": "line",
                "points": [[100, 100], [200, 200]],
                "stroke": "blue",
                "strokeWidth": 2,
            },
        ],
        "duration": 12,
        "tailored_to_interest": user_interest,
        "raw_llm_output": {"source": source, "generated_at": now},
    }


async def generate_lesson(
    topic: str,
    user_interest: str,
    proficiency_level: str = "beginner",
) -> Dict[str, Any]:
    """
    Generate a lesson using an LLM if available, otherwise return a fallback sample.

    This function tries to use GROQ or OpenAI if API keys are present. If not,
    it returns a deterministic mocked lesson to keep the API functional during
    development.
    """
    groq_key = settings.groq_api_key

    print(
        f"[LessonGen] Called with topic='{topic}', "
        f"user_interest='{user_interest}', proficiency='{proficiency_level}'"
    )
    print(f"[LessonGen] GROQ_KEY set: {bool(groq_key)}")

    # If no LLM keys are configured, return a simple fallback lesson
    if not groq_key :
        print("[LessonGen] No LLM API keys found. Returning mock lesson.")
        return _build_mock_lesson(topic, user_interest, source="mock_no_api_keys")

    # Prepare the prompt template
    parser = JsonOutputParser()
    prompt = PromptTemplate(
        template=(
            "You are a private tutor who focuses on conceptual understanding. "
            "Output ONLY valid JSON matching the lesson schema. "
            "Do NOT wrap the lesson in a 'lesson' key. Do NOT use triple backticks. "
            "Generate a lesson on {topic} for a {proficiency_level} student "
            "using examples from {user_interest}. "
            "Respond with a flat JSON object with these keys: "
            "topic, title, narration_script, board_actions, duration, "
            "tailored_to_interest, raw_llm_output. "
            "board_actions should be a list of dicts with animation instructions. "
            "{format_instructions}"
        ),
        input_variables=["topic", "user_interest", "proficiency_level"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Try Groq first, then OpenAI
    llm = None
    llm_name = None

    if groq_key:
        try:
            print("[LessonGen] Attempting to use Groq LLM...")
            

            llm = ChatGroq(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.7,
                groq_api_key=groq_key,
            )
            llm_name = "groq"
        except Exception as e:
            print(f"[LessonGen] Failed to initialize Groq: {e}")

    if not llm:
        print("[LessonGen] Failed to initialize any LLM. Returning mock lesson.")
        return _build_mock_lesson(topic, user_interest, source="llm_init_failed")

    # Generate lesson using the LLM
    try:
        chain = prompt | llm
        raw_response = await chain.ainvoke(
            {
                "topic": topic,
                "user_interest": user_interest,
                "proficiency_level": proficiency_level,
            }
        )

        print(f"[LessonGen] {llm_name.upper()} LLM raw response type: {type(raw_response)}")

        # Extract content from the response (LangChain returns a Message object)
        if hasattr(raw_response, "content"):
            content = raw_response.content
        else:
            content = raw_response

        print(f"[LessonGen] Extracted content: {content[:200]}...")


        # If content is already a dict, ensure raw_llm_output is a dict, then return
        if isinstance(content, dict):
            if "raw_llm_output" in content and isinstance(content["raw_llm_output"], str):
                content["raw_llm_output"] = {"raw": content["raw_llm_output"], "source": f"{llm_name}_string"}
            return content

        # If content is a string, try to parse as JSON or extract lesson fields
        if isinstance(content, str):
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print("[LessonGen] Successfully parsed JSON response.")
                # If parsed is a dict and has lesson fields, return as is
                if all(k in parsed for k in ["topic", "title", "narration_script", "board_actions", "duration"]):
                    if "raw_llm_output" in parsed and isinstance(parsed["raw_llm_output"], str):
                        parsed["raw_llm_output"] = {"raw": parsed["raw_llm_output"], "source": f"{llm_name}_string"}
                    return parsed
                # If parsed is a wrapper (e.g., {"lesson": {...}}), extract
                if "lesson" in parsed and isinstance(parsed["lesson"], dict):
                    lesson = parsed["lesson"]
                    if "raw_llm_output" in lesson and isinstance(lesson["raw_llm_output"], str):
                        lesson["raw_llm_output"] = {"raw": lesson["raw_llm_output"], "source": f"{llm_name}_string"}
                    return lesson
                # If any field is itself a stringified JSON, parse it
                for k in ["narration_script", "board_actions", "raw_llm_output"]:
                    if k in parsed and isinstance(parsed[k], str):
                        try:
                            parsed[k] = json.loads(parsed[k])
                        except Exception:
                            pass
                # If after all this, still not a lesson, fallback
                print("[LessonGen] Parsed JSON but did not find lesson fields. Returning as raw.")
                return {
                    "topic": topic,
                    "title": f"Generated Lesson: {topic}",
                    "narration_script": content,
                    "board_actions": [],
                    "duration": 0,
                    "tailored_to_interest": user_interest,
                    "raw_llm_output": {"raw": content, "source": f"{llm_name}_unparsed"},
                }
            except Exception as e:
                print(f"[LessonGen] Error parsing {llm_name} response as JSON: {e}")
                # Try to find a stringified JSON inside the string
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        inner = json.loads(json_match.group(0))
                        if all(k in inner for k in ["topic", "title", "narration_script", "board_actions", "duration"]):
                            return inner
                    except Exception:
                        pass
                # Return minimal fallback with raw content
                return {
                    "topic": topic,
                    "title": f"Generated Lesson: {topic}",
                    "narration_script": content,
                    "board_actions": [],
                    "duration": 0,
                    "tailored_to_interest": user_interest,
                    "raw_llm_output": {"raw": content, "source": f"{llm_name}_unparsed"},
                }

        # Unexpected content type
        print(f"[LessonGen] Unexpected content type: {type(content)}. Returning mock lesson.")
        return _build_mock_lesson(topic, user_interest, source=f"{llm_name}_unexpected_type")

    except Exception as e:
        print(f"[LessonGen] Exception during {llm_name} LLM call: {e}")
        return _build_mock_lesson(topic, user_interest, source=f"{llm_name}_exception")