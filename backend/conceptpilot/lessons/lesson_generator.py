import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def generate_lesson(topic: str, user_interest: str, proficiency_level: str = "beginner") -> dict:
    """
    Generates a personalized lesson using LangChain and OpenAI,
    including narration script and Konva board actions.
    """
    try:
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("groq_api_key environment variable not set.")

        llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, groq_api_key=groq_api_key)

        parser = JsonOutputParser()

        prompt = PromptTemplate(
            template="""You are ConceptPilot, an AI teacher generating whiteboard lessons.

CRITICAL: Output ONLY valid JSON. No markdown, no code blocks, no explanations.

Example of a GOOD lesson (Forces in Basketball):
{{
  "topic": "Newton's Second Law",
  "title": "Dunking Physics: F=ma in Basketball",
  "narration_script": "When LeBron jumps for a dunk, he's demonstrating F=ma perfectly. His legs apply force to the ground - that's F. His body mass is m, around 250 pounds. The acceleration - how fast he launches upward - depends on F divided by m. More force from his legs means faster acceleration. Let's see this on the court.",
  "board_actions": [
    {{"timestamp": 0, "type": "text", "content": "F = ma (Dunking)", "x": 300, "y": 30, "fontSize": 28, "fill": "#000"}},
    {{"timestamp": 2, "type": "rect", "x": 300, "y": 400, "width": 100, "height": 20, "fill": "#8B4513", "stroke": "#000"}},
    {{"timestamp": 2.2, "type": "text", "content": "Court Floor", "x": 310, "y": 430, "fontSize": 14, "fill": "#000"}},
    {{"timestamp": 3.5, "type": "circle", "x": 350, "y": 380, "radius": 15, "fill": "#FFA500", "stroke": "#000"}},
    {{"timestamp": 3.7, "type": "text", "content": "Player (m=250lb)", "x": 280, "y": 350, "fontSize": 14, "fill": "#000"}},
    {{"timestamp": 5, "type": "line", "points": [350, 380, 350, 320], "stroke": "#FF0000", "strokeWidth": 4}},
    {{"timestamp": 5.2, "type": "text", "content": "Force (F) →", "x": 360, "y": 345, "fontSize": 16, "fill": "#FF0000"}},
    {{"timestamp": 7, "type": "svg_path", "data": "M340 380 Q345 320 350 260", "stroke": "#00FF00", "strokeWidth": 3, "fill": "none"}},
    {{"timestamp": 7.2, "type": "text", "content": "Acceleration (a)", "x": 360, "y": 280, "fontSize": 14, "fill": "#00FF00"}}
  ],
  "duration": 10
}}

Now generate a lesson following this EXACT quality standard.

You are an expert teacher who specializes in making complex concepts easy to understand by giving real world examples based on the student specific interest. Generate a personalized lesson on {{topic}} using examples ONLY from {{user_interest}}.
CRITICAL: The lesson MUST be directly about the provided {{topic}} and nothing else. Do NOT deviate to related but different topics.            
Proficiency level: {{proficiency_level}}
            
CRITICAL RULES (General):
1. Use ONLY examples from {{user_interest}} - no generic examples
2. For simple concepts, use basic shapes (line, text, rect, circle)
3. For complex diagrams, use svg_path with valid SVG path data
4. Each board_action needs: timestamp (seconds), type, and appropriate properties
5. Timestamps should be spaced 1.5-3 seconds apart, and in increasing order.
6. Keep diagrams clear - max 8-10 actions (if possible)
7. Ensure the total duration is reasonably aligned with the narration script length.

DIAGRAM DESIGN RULES (MANDATORY):
1. Canvas is 800x600 - keep all content within bounds
2. Represent forces as ARROWS (lines with direction), not shapes
3. Show motion with curved paths (svg_path), not straight lines
4. Place labels NEXT TO elements, not far away
5. Use spatial metaphors (high = up, low = down)
6. Draw ground/surfaces as thick rectangles at bottom
7. Show cause-effect with visual flow (top→bottom or left→right)
8. Maximum 8 actions - quality over quantity
9. Each action must teach something - no decorative shapes

FOOTBALL-SPECIFIC PHYSICS REPRESENTATIONS:
- Player friction: Draw player (circle/rect), grass (textured base), friction arrows opposing motion
- Ball trajectory: Curved path showing arc, gravity arrow pointing down
- Collision: Two objects, arrows showing before/after velocities
- Sprint mechanics: Multiple positions of player showing acceleration

Output valid JSON:
{{
  "topic": "{{topic}}",
  "title": "short catchy title",
  "narration_script": "engaging 60-90 second narration using {{user_interest}} examples",
  "board_actions": [
    {{"timestamp": 0, "type": "text", "content": "...", "x": 50, "y": 20, "fontSize": 24, "fill": "black"}},
    {{"timestamp": 2.5, "type": "line", "points": [100,100,200,200], "stroke": "blue", "strokeWidth": 2}},
    {{"timestamp": 5, "type": "rect", "x": 100, "y": 100, "width": 50, "height": 50, "stroke": "green", "fill": "rgba(0,255,0,0.2)"}},
    {{"timestamp": 7.5, "type": "circle", "x": 150, "y": 150, "radius": 30, "stroke": "purple", "fill": "rgba(128,0,128,0.2)"}},
    {{"timestamp": 10, "type": "svg_path", "data": "M50 50 L150 50 L100 150 Z", "stroke": "color", "fill": "color", "x": 0, "y": 0}}
  ],
  "duration": 12
}}
            
Canvas dimensions: 800x600. Keep content within bounds.""",
            input_variables=["topic", "user_interest", "proficiency_level"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm

        raw_llm_response_str = chain.invoke({
            "topic": topic,
            "user_interest": user_interest,
            "proficiency_level": proficiency_level
        }).content 

        # Now parse this raw string
        parsed_result = parser.parse(raw_llm_response_str)

        return {
            "parsed_data": parsed_result,
            "raw_response_string": raw_llm_response_str
        }

    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
        print(f"Raw LLM output (might be malformed): {e.doc}")
        raise
    except ValueError as e:
        print(f"Configuration Error: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

if __name__ == '__main__':
    # Example usage:
    # Set your Groq API key as an environment variable, e.g.,
    # export GROQ_API_KEY="gsk_..." (on Linux/macOS)
    # $env:GROQ_API_KEY="gsk_..." (on Windows PowerShell)
    
    # For testing without setting env var, you can temporarily hardcode it:
    # os.environ['GROQ_API_KEY'] = 'YOUR_GROQ_API_KEY_HERE' 

    try:
        print("Generating a lesson on 'Fractions' for 'Cooking' at 'intermediate' level...")
        lesson = generate_lesson("Fractions", "Cooking", "intermediate")
        print("\n--- Generated Lesson ---")
        print(json.dumps(lesson.get("parsed_data", {}), indent=2))
        print(f"\nNarration Script Length: {len(lesson.get('parsed_data', {}).get('narration_script', ''))} characters")
        print(f"Number of Board Actions: {len(lesson.get('parsed_data', {}).get('board_actions', []))}")
        
        print("\nGenerating another lesson on 'Gravity' for 'Space Exploration' at 'advanced' level...")
        lesson2 = generate_lesson("Gravity", "Space Exploration", "advanced")
        print("\n--- Generated Lesson 2 ---")
        print(json.dumps(lesson2.get("parsed_data", {}), indent=2))
        
    except Exception as e:
        print(f"Failed to generate lesson: {e}")
