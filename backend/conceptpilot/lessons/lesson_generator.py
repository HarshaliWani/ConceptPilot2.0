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
            template="""You are an educational content creator. Generate a personalized lesson on {topic} using examples ONLY from {user_interest}.
            
            Proficiency level: {proficiency_level}
            
            CRITICAL RULES:
            1. Use ONLY examples from {user_interest} - no generic examples
            2. For simple concepts, use basic shapes (line, text, rect, circle)
            3. For complex diagrams, use svg_path with valid SVG path data
            4. Each board_action needs: timestamp (seconds), type, and appropriate properties
            5. Timestamps should be spaced 1.5-3 seconds apart, and in increasing order.
            6. Keep diagrams clear - max 8-10 actions (if possible)
            7. Ensure the total duration is reasonably aligned with the narration script length.
            
            Output valid JSON:
            {{
              "topic": "{topic}",
              "title": "short catchy title",
              "narration_script": "engaging 60-90 second narration using {user_interest} examples",
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

        chain = prompt | llm | parser

        result = chain.invoke({
            "topic": topic,
            "user_interest": user_interest,
            "proficiency_level": proficiency_level
        })

        # Ensure the output is a dictionary and handles potential parsing nuances
        if isinstance(result, str):
            result = json.loads(result)

        return result

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
        print(json.dumps(lesson, indent=2))
        print(f"\nNarration Script Length: {len(lesson.get('narration_script', ''))} characters")
        print(f"Number of Board Actions: {len(lesson.get('board_actions', []))}")
        
        print("\nGenerating another lesson on 'Gravity' for 'Space Exploration' at 'advanced' level...")
        lesson2 = generate_lesson("Gravity", "Space Exploration", "advanced")
        print("\n--- Generated Lesson 2 ---")
        print(json.dumps(lesson2, indent=2))
        
    except Exception as e:
        print(f"Failed to generate lesson: {e}")
