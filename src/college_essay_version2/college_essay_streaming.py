# File: college_essay_streaming.py

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from college_essay_version2.crew import CollegeEssayVersion2Crew
from crewai_tools import FileReadTool
import asyncio

app = FastAPI()

class StreamingCollegeEssayCrewRunner(CollegeEssayVersion2Crew):
    def get_file_content(self):
        file_reader_tool = FileReadTool(file_path="/home/albert/Downloads/rika-pinto-resume.md")
        return file_reader_tool.run()

async def college_essay_stream():
    crew_runner = StreamingCollegeEssayCrewRunner()
    file_content = crew_runner.get_file_content()
    yield f"File content loaded. Length: {len(file_content)} characters\n"
    
    inputs = {
        'file_content': file_content,
        'program': 'Business',
        'output_essay': 'essay',
        'student': 'Rika Pinto',
    }
    
    for input_key, input_value in inputs.items():
        yield f"Input: {input_key} - {input_value[:50]}...\n"  # Truncate long values
        await asyncio.sleep(0.1)
    
    yield "Starting crew execution...\n"
    custom_crew = crew_runner.crew()
    
    # Simulate the start of each agent's work
    for agent in custom_crew.agents:
        yield f"Agent {agent.role} is starting work\n"
        await asyncio.sleep(0.5)

    # Execute the crew
    result = custom_crew.kickoff(inputs=inputs)
    yield f"Crew execution completed. Result: {result}\n"

    # Convert the generated essay to PDF
    input_file = "/home/albert/Documents/college_essay_version2/essay.md"
    output_file = "/home/albert/Documents/college_essay_version2/essay.pdf"
    yield f"Converting essay to PDF: {input_file} -> {output_file}\n"
    pdf_result = crew_runner.convert_to_pdf(input_file, output_file)
    yield f"PDF Conversion Result: {pdf_result}\n"

@app.get("/stream_college_essay")
async def stream_college_essay():
    return StreamingResponse(college_essay_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)