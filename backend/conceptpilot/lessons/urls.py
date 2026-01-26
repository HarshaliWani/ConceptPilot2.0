from django.urls import path
from .views import get_test_lesson, get_svg_test_lesson, generate_ai_lesson, get_lesson 

urlpatterns = [
    path('test-lesson/', get_test_lesson, name='test-lesson'),
    path('generate/', generate_ai_lesson, name='generate-lesson'),
    path('svg-test-lesson/', get_svg_test_lesson, name='svg-test-lesson'),
    path('<uuid:lesson_id>/', get_lesson, name='get-lesson'), 
]