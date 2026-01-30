from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils import timezone
from .models import Lesson 
from .lesson_generator import generate_lesson
from .serializers import LessonSerializer 


@api_view(['GET'])
def get_test_lesson(request):
    """API view that returns a hardcoded Pythagorean Theorem test lesson."""
    lesson_data = {
        'id': 1,
        'topic': 'Pythagorean Theorem',
        'tailored_to_interest': 'Mathematics',
        'title': 'Understanding the Pythagorean Theorem',
        'narration_script': "Let's explore the Pythagorean Theorem. We'll draw a right triangle. First, the vertical side. Now the horizontal side. And finally, the hypotenuse. This is side A, this is side B, and this is side C. Remember: A squared plus B squared equals C squared.",
        'board_actions': [
            {'type': 'text', 'content': 'Pythagorean Theorem', 'x': 50, 'y': 20, 'fontSize': 24, 'fill': 'black', 'timestamp': 0},
            {'type': 'line', 'points': [150, 200, 150, 350], 'stroke': 'blue', 'strokeWidth': 3, 'timestamp': 2.5},
            {'type': 'line', 'points': [150, 350, 350, 350], 'stroke': 'blue', 'strokeWidth': 3, 'timestamp': 4.0},
            {'type': 'line', 'points': [150, 200, 350, 350], 'stroke': 'red', 'strokeWidth': 3, 'timestamp': 5.5},
            {'type': 'text', 'content': 'a', 'x': 130, 'y': 260, 'fontSize': 20, 'fill': 'blue', 'timestamp': 7.0},
            {'type': 'text', 'content': 'b', 'x': 240, 'y': 360, 'fontSize': 20, 'fill': 'blue', 'timestamp': 8.0},
            {'type': 'text', 'content': 'c', 'x': 240, 'y': 260, 'fontSize': 20, 'fill': 'red', 'timestamp': 9.0},
            {'type': 'text', 'content': 'a² + b² = c²', 'x': 400, 'y': 270, 'fontSize': 22, 'fill': 'black', 'timestamp': 10.5}
        ],
        'audio_url': None,
        'duration': 12,
        'created_at': timezone.now()
    }
    return Response(lesson_data, status=200)


@api_view(['GET'])
def get_svg_test_lesson(request):
    """API view that returns a hardcoded Quadratic Functions test lesson with SVG path."""
    lesson_data = {
        'id': 2, # Changed ID to differentiate
        'topic': "Quadratic Functions",
        'tailored_to_interest': "Mathematics",
        'title': "Understanding Parabolas with SVG",
        'narration_script': "Let's explore quadratic functions. First, we draw our axes. Now watch as the parabola appears. Notice the vertex at the top. This parabola opens upward because the coefficient is positive.",
        'board_actions': [
            {"type": "text", "content": "Quadratic Function: y = x²", "x": 50, "y": 20, "fontSize": 24, "fill": "black", "timestamp": 0},
            {"type": "line", "points": [50, 300, 750, 300], "stroke": "#ccc", "strokeWidth": 1, "timestamp": 1}, # x-axis
            {"type": "line", "points": [400, 50, 400, 550], "stroke": "#ccc", "strokeWidth": 1, "timestamp": 1.5}, # y-axis
            {"type": "svg_path", "data": "M 400 300 Q 400 100 500 100 Q 600 100 600 300 Q 600 500 500 500 Q 400 500 400 300", "stroke": "blue", "strokeWidth": 3, "fill": "rgba(100,150,255,0.2)", "timestamp": 2.5},
            {"type": "text", "content": "Vertex", "x": 380, "y": 80, "fontSize": 16, "fill": "red", "timestamp": 5},
            {"type": "circle", "x": 400, "y": 100, "radius": 5, "fill": "red", "timestamp": 6},
            {"type": "text", "content": "This parabola opens upward", "x": 450, "y": 250, "fontSize": 18, "fill": "blue", "timestamp": 7}
        ],
        'audio_url': None,
        'duration': 10,
        'created_at': timezone.now()
    }
    return Response(lesson_data, status=200)

@api_view(['GET'])
def get_lesson(request, lesson_id):
    """
    API endpoint to retrieve a single lesson by its ID.
    """
    # Use get_object_or_404 to raise a 404 if the lesson is not found
    lesson = get_object_or_404(Lesson, id=lesson_id)
    serializer = LessonSerializer(lesson)
    return Response(serializer.data)

@api_view(['POST'])
def generate_ai_lesson(request):
    """
    API endpoint to generate a lesson using AI based on user input and save it to the database.
    Expects JSON body: {"topic": str, "user_interest": str, "proficiency_level": str (optional)}
    """
    topic = request.data.get('topic')
    user_interest = request.data.get('user_interest')
    proficiency_level = request.data.get('proficiency_level', 'beginner') # Default to 'beginner'

    # Validate required fields
    if not topic or not user_interest:
        return Response(
            {"error": "Missing required fields: 'topic' and 'user_interest' are necessary."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get both parsed data and the raw string from the generator
        generation_output = generate_lesson(topic, user_interest, proficiency_level)
        generated_data = generation_output['parsed_data']
        raw_llm_output_str = generation_output['raw_response_string']

        # Create and save a new Lesson object
        lesson = Lesson(
            topic=generated_data['topic'],
            tailored_to_interest=user_interest,
            title=generated_data['title'],
            narration_script=generated_data['narration_script'],
            board_actions=generated_data['board_actions'],
            audio_url=None,
            duration=generated_data['duration'],
            raw_llm_output=raw_llm_output_str, # SAVE THE RAW OUTPUT
        )
        lesson.save()

        # Return the newly created lesson's data.
        # You might want to use a serializer (like LessonSerializer) here for consistency.
        serializer = LessonSerializer(lesson)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    except ValueError as e:
        # Catch specific errors from lesson_generator (e.g., OPENAI_API_KEY not set)
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        # Catch any other unexpected errors during lesson generation or saving
        return Response(
            {"error": f"An unexpected error occurred during lesson generation or saving: {e}"},
            status=status.HTTP_400_BAD_REQUEST
        )