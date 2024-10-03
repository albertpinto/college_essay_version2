#!/usr/bin/env python
import sys
from college_essay_version2.crew import CollegeEssayVersion2Crew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding necessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    crew = CollegeEssayVersion2Crew()
    file_content = crew.get_file_content()
    inputs = {
        'file_content': file_content,
        'program': 'Business',
        'output_essay': 'essay',
        'student': 'Rika Pinto',
    }
    for input in inputs:
        print((input, inputs[input]))
    CollegeEssayVersion2Crew().crew().kickoff(inputs=inputs)
    # Convert the generated essay to PDF
    input_file = "/home/albert/Documents/college_essay_version2/essay.md"  # This should match the output_file in essay_task
    output_file = "/home/albert/Documents/college_essay_version2/essay.pdf"
    pdf_result = crew.convert_to_pdf(input_file, output_file)
    #print(pdf_result)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        "openai_model_name": "gpt-4o"
    }
    try:
        CollegeEssayVersion2Crew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        CollegeEssayVersion2Crew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        CollegeEssayVersion2Crew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
