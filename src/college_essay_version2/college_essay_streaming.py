# college_essay_streaming.py

import os
import base64
import shutil
import asyncio
from fastapi import FastAPI, Query, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from college_essay_version2.crew import CollegeEssayVersion2Crew
from crewai_tools import FileReadTool

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class StreamingCollegeEssayCrewRunner(CollegeEssayVersion2Crew):
    def __init__(self, model):
        super().__init__(model)

    def get_file_content(self, file_path):
        """Read content from a file using FileReadTool."""
        file_reader_tool = FileReadTool(file_path=file_path)
        return file_reader_tool.run()

async def college_essay_stream(program: str, student: str, resume_file_path: str, model: str):
    """
    Generator function to stream the college essay creation process.
    Yields status updates and the final PDF content.
    """
    crew_runner = StreamingCollegeEssayCrewRunner(model)
    
    # Load file content
    file_content = crew_runner.get_file_content(resume_file_path)
    yield f"data: File content loaded. Length: {len(file_content)} characters\n\n"
    
    # Prepare inputs
    inputs = {
        'file_content': file_content,
        'program': program,
        'output_essay': "essay",
        'student': student,
        'model': model  # Include the selected model in the inputs
    }
    
    # Stream input information
    for input_key, input_value in inputs.items():
        yield f"data: Input: {input_key} - {input_value[:50]}...\n\n"
        await asyncio.sleep(0.1)
    
    # Execute crew tasks
    yield "data: Starting crew execution...\n\n"
    custom_crew = crew_runner.crew()
    
    for agent in custom_crew.agents:
        yield f"data: Agent {agent.role} is starting work\n\n"
        await asyncio.sleep(0.5)

    result = custom_crew.kickoff(inputs=inputs)
    yield f"data: Crew execution completed. Result: {result}\n\n"

    # Convert essay to PDF
    input_file = "/home/albert/Documents/college_essay_version2/essay.md"
    output_file = f"/home/albert/Documents/college_essay_version2/essay.pdf"
    yield f"data: Converting essay to PDF: {input_file} -> {output_file}\n\n"
    pdf_result = crew_runner.convert_to_pdf(input_file, output_file)
    yield f"data: PDF Conversion Result: {pdf_result}\n\n"

    # Stream PDF content
    with open(output_file, "rb") as pdf_file:
        pdf_content = pdf_file.read()
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        yield f"data: PDF_CONTENT:{pdf_base64}\n\n"

    yield "data: Streaming completed\n\n"

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Endpoint to handle resume file uploads.
    Saves the file to the upload directory and returns the file path.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"file_path": file_path})

@app.get("/stream_college_essay")
async def stream_college_essay(
    program: str = Query(..., description="Program name"),
    student: str = Query(..., description="Student name"),
    resumeFilePath: str = Query(..., description="Path to uploaded resume file"),
    model: str = Query(..., description="Selected language model")
):
    """
    Endpoint to stream the college essay generation process.
    Returns a StreamingResponse with real-time updates.
    """
    return StreamingResponse(
        college_essay_stream(program, student, resumeFilePath, model),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)