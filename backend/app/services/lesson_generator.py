"""Lesson generator service (wrapper around LangChain)."""
import json
import re
from typing import Dict, Any
from datetime import datetime

from app.core.config import get_settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.services.tts_service import generate_audio

settings = get_settings()


def _parse_duration(duration_value) -> float:
    """Parse duration value to float, handling strings with units."""
    if isinstance(duration_value, (int, float)):
        return float(duration_value)
    
    if isinstance(duration_value, str):
        # Extract number from strings like "6 minutes", "180 seconds", "3.5"
        import re
        number_match = re.search(r'([0-9.]+)', duration_value)
        if number_match:
            num = float(number_match.group(1))
            # Convert minutes to seconds if "minute" is in the string
            if 'minute' in duration_value.lower():
                return num * 60
            return num
    
    return 180.0  # Default 3 minutes


def _validate_and_fix_board_actions(board_actions):
    """Validate and fix board_actions to match Konva.js format."""
    print(f"[DEBUG] Original board_actions: {board_actions}")
    print(f"[DEBUG] Board actions type: {type(board_actions)}")
    
    if not isinstance(board_actions, list):
        print(f"[DEBUG] Not a list, returning empty array")
        return []
    
    print(f"[DEBUG] Board actions list has {len(board_actions)} items")
    fixed_actions = []
    max_y = 0  # Track max Y coordinate for clearing logic
    
    for i, action in enumerate(board_actions):
        print(f"[DEBUG] Processing action {i}: {action}")
        print(f"[DEBUG] Action type: {type(action)}")
        
        if not isinstance(action, dict):
            print(f"[DEBUG] Action {i} is not a dict, skipping")
            continue
            
        if "type" not in action:
            print(f"[DEBUG] Action {i} missing 'type' field, skipping")
            continue
            
        # Only auto-assign timestamps if completely missing (let LLM control timing)
        if "timestamp" not in action:
            # More intelligent timestamp assignment based on position in lesson
            base_time = i * 1.5  # 1.5 seconds per action (slower than before)
            action["timestamp"] = base_time
            print(f"[DEBUG] Action {i} missing timestamp, assigned {action['timestamp']}")
            
        # Ensure timestamp is a number
        try:
            action["timestamp"] = float(action["timestamp"])
        except (ValueError, TypeError) as e:
            print(f"[DEBUG] Action {i} timestamp conversion failed: {e}, skipping")
            continue
            
        # Check if we need to clear the board (when Y exceeds canvas height)
        if "y" in action:
            current_y = float(action["y"])
            max_y = max(max_y, current_y)
            
            # Clear board when content goes below 500px (canvas is 600px) OR when we have too many elements
            should_clear = (
                (current_y > 500 and len(fixed_actions) > 10) or  # Y position trigger
                (len(fixed_actions) > 0 and len(fixed_actions) % 15 == 0)  # Element count trigger
            )
            
            if should_clear:
                clear_action = {
                    "timestamp": action["timestamp"] - 1,  # Clear 1 second before new content
                    "type": "clear",
                    "fade_duration": 0.5
                }
                fixed_actions.append(clear_action)
                print(f"[DEBUG] Inserted clear action at timestamp {clear_action['timestamp']} (y={current_y}, elements={len(fixed_actions)})")
        
        # Fix points format for lines (flatten nested arrays if needed)
        if action["type"] == "line" and "points" in action:
            points = action["points"]
            if isinstance(points, list) and len(points) > 0:
                # If nested arrays like [[x1,y1], [x2,y2]], flatten to [x1,y1,x2,y2]
                if isinstance(points[0], list):
                    flattened = []
                    for point in points:
                        if isinstance(point, list) and len(point) >= 2:
                            flattened.extend([float(point[0]), float(point[1])])
                    action["points"] = flattened
                else:
                    # Ensure all points are numbers
                    action["points"] = [float(p) for p in points]
        
        # Ensure numeric properties are numbers where needed
        numeric_props = ["x", "y", "fontSize", "strokeWidth", "width", "height", "radius"]
        for prop in numeric_props:
            if prop in action and action[prop] is not None:
                try:
                    action[prop] = float(action[prop])
                except (ValueError, TypeError):
                    pass
                    
        fixed_actions.append(action)
        print(f"[DEBUG] Action {i} validated and added to fixed_actions")
    
    print(f"[DEBUG] Final fixed_actions count: {len(fixed_actions)}")
    return fixed_actions


def _clean_narration_for_tts(narration: str) -> str:
    """Remove diagram/drawing instructions from narration before sending to TTS."""
    import re
    lines = narration.split('\n')
    cleaned = []
    # Patterns that indicate diagram/board instructions rather than spoken content
    skip_patterns = [
        r'\b(draw|sketch|write on|put on|place on|add to)\s+(a |the )?(board|canvas|whiteboard|diagram)',
        r'\b(drawing|writing|placing|adding)\s+(a |the )?(rectangle|circle|line|arrow|box|shape|text)',
        r'^\s*\[.*\]\s*$',  # Lines that are just [bracketed stage directions]
        r'^\s*\(.*\)\s*$',  # Lines that are just (parenthetical stage directions)
        r'\blet me (draw|write|sketch|illustrate|show you on)',
        r'\bas (I |we )?(draw|write|sketch|illustrate)',
        r"\bon the (board|canvas|whiteboard|screen)",
        r'\btimestamp\b.*\btype\b',  # JSON-like board action descriptions
    ]
    combined = re.compile('|'.join(skip_patterns), re.IGNORECASE)
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if combined.search(stripped):
            continue
        cleaned.append(line)
    result = '\n'.join(cleaned).strip()
    return result if result else narration  # Fallback to original if everything stripped


def _build_mock_lesson(topic: str, user_interest: str, source: str) -> Dict[str, Any]:
    """Create a deterministic mock lesson for fallback scenarios."""
    now = datetime.utcnow().isoformat()
    return {
        "topic": topic,
        "title": f"Understanding {topic}",
        "narration_script": (
            f"Today we'll explore {topic} using examples from {user_interest}. "
            f"Let me start by writing the key concept on the board, then we'll draw "
            f"a simple diagram to show how it works in real life."
        ),
        "board_actions": [
            # Write main topic
            {
                "timestamp": 0,
                "type": "text",
                "content": topic,
                "x": 350,
                "y": 50,
                "fontSize": 28,
                "fill": "black",
            },
            # Draw a simple diagram box
            {
                "timestamp": 5,
                "type": "rect",
                "x": 200,
                "y": 150,
                "width": 400,
                "height": 200,
                "stroke": "blue",
                "strokeWidth": 3,
                "fill": "none",
            },
            # Add key term inside
            {
                "timestamp": 8,
                "type": "text",
                "content": "Key Concept",
                "x": 360,
                "y": 180,
                "fontSize": 20,
                "fill": "blue",
            },
            # Draw arrow pointing to explanation
            {
                "timestamp": 12,
                "type": "line",
                "points": [400, 200, 500, 280],
                "stroke": "red",
                "strokeWidth": 3,
            },
            # Arrow head
            {
                "timestamp": 12,
                "type": "line", 
                "points": [490, 270, 500, 280, 495, 290],
                "stroke": "red",
                "strokeWidth": 3,
            },
            # Related concept
            {
                "timestamp": 15,
                "type": "text",
                "content": f"{user_interest} Example",
                "x": 520,
                "y": 290,
                "fontSize": 18,
                "fill": "green",
            },
        ],
        "duration": 20,
        "tailored_to_interest": user_interest,
        "grade_level": "middle school",
        "raw_llm_output": {"source": source, "generated_at": now},
        "audio_url": None,
    }


async def generate_lesson(
    topic: str,
    user_interest: str,
    proficiency_level: str = "beginner",
    grade_level: str = "middle school",
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

    # Use ChatPromptTemplate for role separation
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert visual educator who creates engaging, well-timed whiteboard lessons.

=== LESSON STRUCTURE ===
- Write a clear, spoken narration (what the teacher says)
- Create synchronized visual actions (what appears on the whiteboard)
- Make the lesson engaging and memorable

=== NARRATION RULES ===
Write ONLY spoken content (like a podcast or lecture)
Start with an introduction to the topic, then explain key concepts step-by-step, cover theory, definitions, key rules or formulas and finally explain with analogies and examples from student's interest/hobby.
Don't describe visual actions ("Now I'll draw..." "Let me write...")

=== VISUAL ACTIONS ===
- Synchronize timestamps with when concepts are mentioned in narration
- Use varied visual elements (text, shapes, arrows) for clarity
- Keep main content in upper 400px (y < 400) of 800x600 canvas

Action types:
- text: Key terms/labels (fontSize 18-32, varied colors)
- line: Arrows/connections (points [x1,y1,x2,y2], colorful strokes)
- rect: Boxes/containers (varied fills like lightblue, lightgreen)
- circle: Concepts/objects (varied fills, meaningful colors)
         
=== TECHNICAL SPECS ===
Canvas: 800x600 pixels, (0,0) = top-left
         
=== PERSONALIZATION ===
If student has a hobby/interest, incorporate relevant analogies naturally.

Example timing breakdown:
- Narration: "Let's start with the main concept of [TERM appears at 5s] semiconductors. 
  These materials [diagram starts at 8s] have unique properties..."
- Board: timestamp:5 → write "Semiconductors", timestamp:8 → draw diagram

OUTPUT FORMAT:
{{
  "topic": "...",
  "title": "...",
  "narration_script": "Full explanation with natural pacing",
  "board_actions": [
    {{"timestamp": 0, "type": "text", "content": "Main Topic", "x": 300, "y": 50, "fontSize": 28, "fill": "darkblue"}},
    {{"timestamp": 8, "type": "circle", "x": 200, "y": 150, "radius": 60, "stroke": "red", "strokeWidth": 3, "fill": "lightcoral"}}
  ],
  "duration": "estimated_seconds",
  "tailored_to_interest": "...",
  "grade_level": "..."
}}


=== EXAMPLE: Teaching "Photosynthesis" ===
Narration: "Today we'll learn about photosynthesis. The process starts when sunlight hits the leaf..."
Board:
- t=0: "Photosynthesis" (darkgreen, large)
- t=8: Sun symbol (yellow circle)
- t=12: Leaf shape (green)
- t=15: Arrow sun→leaf (orange)

Remember: BALANCE timing precision with visual creativity!"""),
        
        ("user", """Generate a lesson on {topic} for a {proficiency_level} student in {grade_level}.

Student's hobby/interest: {user_interest}
IMPORTANT: If the student has a specific hobby (not "general interests"), incorporate creative analogies, examples, or metaphors related to their hobby to make the lesson more engaging and relatable. If it's "general interests", use widely accessible examples.

Generate the lesson now:"""),
        
        ("assistant", "{{")
    ])

    # Try Groq first, then OpenAI
    llm = None
    llm_name = None

    if groq_key:
        try:
            print("[LessonGen] Attempting to use Groq LLM...")
            

            llm = ChatGroq(
                model="openai/gpt-oss-120b",
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
                "user_interest": user_interest or "general interests",  # Fallback if empty
                "proficiency_level": proficiency_level,
                "grade_level": grade_level,
            }
        )

        print(f"[LessonGen] {llm_name.upper()} LLM raw response type: {type(raw_response)}")

        # Extract content from the response (LangChain returns a Message object)
        if hasattr(raw_response, "content"):
            content = raw_response.content
        else:
            content = raw_response


        # If content is already a dict, ensure raw_llm_output is a dict, then return
        if isinstance(content, dict):
            # Validate and fix board_actions format
            if "board_actions" in content:
                content["board_actions"] = _validate_and_fix_board_actions(content["board_actions"])
            # Parse and fix duration
            if "duration" in content:
                content["duration"] = _parse_duration(content["duration"])
            if "raw_llm_output" in content and isinstance(content["raw_llm_output"], str):
                content["raw_llm_output"] = {"raw": content["raw_llm_output"], "source": f"{llm_name}_string"}
            
            # Generate audio for lesson (clean narration first)
            lesson_id = f"{topic.replace(' ', '')}{int(datetime.utcnow().timestamp())}"
            clean_text = _clean_narration_for_tts(content["narration_script"])
            audio_result = await generate_audio(clean_text, lesson_id)
            if audio_result is not None:
                audio_url, actual_duration = audio_result
                content["audio_url"] = audio_url
                content["duration"] = actual_duration  # Use actual audio duration
                print(f"[LessonGen] Audio generated: {audio_url} (duration: {actual_duration:.1f}s)")
            else:
                print("[LessonGen] Audio generation failed, continuing without audio")
            
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
            
            # Clean up markdown formatting that breaks JSON
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove **bold** 
            content = re.sub(r'\*(.*?)\*', r'\1', content)      # Remove *italic*
            content = re.sub(r'`(.*?)`', r'\1', content)        # Remove `code`
            
            # Prepend opening brace if missing (from assistant priming)
            if not content.startswith("{"):
                content = "{" + content

            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print("[LessonGen] Successfully parsed JSON response.")
                # If parsed is a dict and has lesson fields, return as is
                if all(k in parsed for k in ["topic", "title", "narration_script", "board_actions", "duration"]):
                    # Validate and fix board_actions format
                    if "board_actions" in parsed:
                        parsed["board_actions"] = _validate_and_fix_board_actions(parsed["board_actions"])
                    # Parse and fix duration
                    if "duration" in parsed:
                        parsed["duration"] = _parse_duration(parsed["duration"])
                    if "raw_llm_output" in parsed and isinstance(parsed["raw_llm_output"], str):
                        parsed["raw_llm_output"] = {"raw": parsed["raw_llm_output"], "source": f"{llm_name}_string"}
                    
                    # Generate audio for lesson
                    lesson_id = f"{topic.replace(' ', '')}{int(datetime.utcnow().timestamp())}"
                    clean_text = _clean_narration_for_tts(parsed["narration_script"])
                    audio_result = await generate_audio(clean_text, lesson_id)
                    if audio_result is not None:
                        audio_url, actual_duration = audio_result
                        parsed["audio_url"] = audio_url
                        parsed["duration"] = actual_duration  # Use actual audio duration
                        print(f"[LessonGen] Audio generated: {audio_url} (duration: {actual_duration:.1f}s)")
                    else:
                        print("[LessonGen] Audio generation failed, continuing without audio")
                    
                    return parsed
                # If parsed is a wrapper (e.g., {"lesson": {...}}), extract
                if "lesson" in parsed and isinstance(parsed["lesson"], dict):
                    lesson = parsed["lesson"]
                    # Validate and fix board_actions format
                    if "board_actions" in lesson:
                        lesson["board_actions"] = _validate_and_fix_board_actions(lesson["board_actions"])
                    # Parse and fix duration
                    if "duration" in lesson:
                        lesson["duration"] = _parse_duration(lesson["duration"])
                    if "raw_llm_output" in lesson and isinstance(lesson["raw_llm_output"], str):
                        lesson["raw_llm_output"] = {"raw": lesson["raw_llm_output"], "source": f"{llm_name}_string"}
                    
                    # Generate audio for lesson
                    lesson_id = f"{topic.replace(' ', '')}{int(datetime.utcnow().timestamp())}"
                    clean_text = _clean_narration_for_tts(lesson["narration_script"])
                    audio_result = await generate_audio(clean_text, lesson_id)
                    if audio_result is not None:
                        audio_url, actual_duration = audio_result
                        lesson["audio_url"] = audio_url
                        lesson["duration"] = actual_duration  # Use actual audio duration
                        print(f"[LessonGen] Audio generated: {audio_url} (duration: {actual_duration:.1f}s)")
                    else:
                        print("[LessonGen] Audio generation failed, continuing without audio")
                    
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
                    "duration": 180.0,
                    "tailored_to_interest": user_interest,
                    "raw_llm_output": {"raw": content, "source": f"{llm_name}_unparsed"},
                }
            except Exception as e:
                print(f"[LessonGen] Error parsing {llm_name} response as JSON: {e}")
                # Try to find a stringified JSON inside the string
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        inner = json.loads(json_match.group(0))
                        if all(k in inner for k in ["topic", "title", "narration_script", "board_actions", "duration"]):
                            # Validate and fix board_actions format
                            if "board_actions" in inner:
                                inner["board_actions"] = _validate_and_fix_board_actions(inner["board_actions"])
                            # Parse and fix duration
                            if "duration" in inner:
                                inner["duration"] = _parse_duration(inner["duration"])
                            
                            # Generate audio for lesson
                            lesson_id = f"{topic.replace(' ', '')}{int(datetime.utcnow().timestamp())}"
                            clean_text = _clean_narration_for_tts(inner["narration_script"])
                            audio_result = await generate_audio(clean_text, lesson_id)
                            if audio_result is not None:
                                audio_url, actual_duration = audio_result
                                inner["audio_url"] = audio_url
                                inner["duration"] = actual_duration  # Use actual audio duration
                                print(f"[LessonGen] Audio generated: {audio_url} (duration: {actual_duration:.1f}s)")
                            else:
                                print("[LessonGen] Audio generation failed, continuing without audio")
                            
                            return inner
                    except Exception:
                        pass
                # Return minimal fallback with raw content
                return {
                    "topic": topic,
                    "title": f"Generated Lesson: {topic}",
                    "narration_script": content,
                    "board_actions": [],
                    "duration": 180.0,
                    "tailored_to_interest": user_interest,
                    "raw_llm_output": {"raw": content, "source": f"{llm_name}_unparsed"},
                }

        # Unexpected content type
        print(f"[LessonGen] Unexpected content type: {type(content)}. Returning mock lesson.")
        return _build_mock_lesson(topic, user_interest, source=f"{llm_name}_unexpected_type")

    except Exception as e:
        print(f"[LessonGen] Exception during {llm_name} LLM call: {e}")
        return _build_mock_lesson(topic, user_interest, source=f"{llm_name}_exception")