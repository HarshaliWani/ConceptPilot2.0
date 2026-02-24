# backend/app/services/flashcard_generator.py
import json
import re
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from ..core.config import get_settings

settings = get_settings()


async def generate_flashcards(topic: str, count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate flashcards using LLM for a given topic.
    
    Args:
        topic: The topic to generate flashcards for
        count: Number of flashcards to generate (default 10)
        
    Returns:
        List of flashcard dictionaries with front, back, difficulty, explanation
    """
    
    prompt_template = PromptTemplate(
        input_variables=["topic", "count"],
        template="""You are an expert educational content creator. Generate {count} high-quality flashcards for the following topic:

Topic: {topic}

Create flashcards that:
1. Cover key concepts, definitions, formulas, and applications
2. Vary in difficulty (easy, medium, hard)
3. Are clear, concise, and educational
4. Include practical examples where relevant

Return ONLY a valid JSON array with this exact structure (no markdown, no extra text):
[
  {{
    "front": "Clear, concise question or term",
    "back": "Comprehensive answer or definition (2-4 sentences)",
    "difficulty": "easy|medium|hard",
    "explanation": "Brief context, mnemonic, or tip to help remember (optional, 1-2 sentences)"
  }}
]

Guidelines:
- Front side: Ask specific questions or state terms clearly
- Back side: Provide accurate, complete answers
- Difficulty: Distribute as 40% easy, 40% medium, 20% hard
- Explanation: Add helpful tips, mnemonics, or real-world connections
- Make it engaging and memorable

Generate {count} flashcards now:"""
    )
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.groq_api_key,
        temperature=0.7,
        max_tokens=4000
    )
    
    chain = prompt_template | llm
    
    try:
        response = await chain.ainvoke({
            "topic": topic,
            "count": count
        })
        
        # Extract text from response
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Try to extract JSON from the response
        # Remove markdown code blocks if present
        json_text = re.sub(r'```json\s*', '', response_text)
        json_text = re.sub(r'```\s*', '', json_text)
        json_text = json_text.strip()
        
        # Parse JSON
        flashcards = json.loads(json_text)
        
        # Validate structure
        if not isinstance(flashcards, list):
            raise ValueError("Response is not a list")
        
        valid_flashcards = []
        for card in flashcards:
            if not isinstance(card, dict):
                continue
            if 'front' not in card or 'back' not in card:
                continue
            
            # Normalize difficulty
            difficulty = card.get('difficulty', 'medium').lower()
            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'
            
            valid_flashcards.append({
                'front': card['front'].strip(),
                'back': card['back'].strip(),
                'difficulty': difficulty,
                'explanation': card.get('explanation', '').strip() or None
            })
        
        if len(valid_flashcards) == 0:
            raise ValueError("No valid flashcards generated")
        
        return valid_flashcards
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text[:500]}")
        raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        raise ValueError(f"Failed to generate flashcards: {str(e)}")
