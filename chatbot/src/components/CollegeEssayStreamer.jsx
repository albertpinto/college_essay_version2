import React, { useState, useRef, useCallback } from 'react';

const CollegeEssayStreamer = () => {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [pdfContent, setPdfContent] = useState(null);
  const eventSourceRef = useRef(null);

  const [program, setProgram] = useState('');
  const [student, setStudent] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo');

  const models = [
    'o1-preview', 'o1-mini', 'gpt-4o', 'claude-2.5', 'gpt-3.5-turbo', 
    'Mistral-nemo', 'Llama3', 'Mistral'
  ];

  const startStreaming = useCallback(async () => {
    if (!program || !student || !resumeFile || !selectedModel) {
      setError('Please fill in all fields, upload a resume, and select a model before starting.');
      return;
    }

    setIsStreaming(true);
    setMessages([]);
    setError(null);
    setPdfContent(null);

    // First, upload the resume file
    const formData = new FormData();
    formData.append('file', resumeFile);
    
    try {
      const uploadResponse = await fetch('http://localhost:8000/upload_resume', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Resume upload failed');
      }

      const uploadResult = await uploadResponse.json();
      const resumeFilePath = uploadResult.file_path;

      // Now start the SSE connection with all parameters
      const params = new URLSearchParams({ 
        program, 
        student, 
        resumeFilePath,
        model: selectedModel
      }).toString();
      eventSourceRef.current = new EventSource(`http://localhost:8000/stream_college_essay?${params}`);

      eventSourceRef.current.onmessage = (event) => {
        const data = event.data.replace(/^data: /, '').trim();
        if (data.startsWith('PDF_CONTENT:')) {
          const base64Content = data.replace('PDF_CONTENT:', '');
          setPdfContent(base64Content);
        } else if (data) {
          setMessages(prev => [...prev, { text: data, type: 'bot' }]);
        }
      };

      eventSourceRef.current.onerror = (error) => {
        console.error('EventSource failed:', error);
        setError('Failed to connect to the streaming service. Please check the server status.');
        setIsStreaming(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
        }
      };

      eventSourceRef.current.onopen = () => {
        console.log('Connection opened');
      };
    } catch (err) {
      setError(`Failed to start essay generation: ${err.message}`);
      setIsStreaming(false);
    }
  }, [program, student,resumeFile, selectedModel]);

  const handleClear = useCallback(() => {
    setMessages([]);
    setError(null);
    setPdfContent(null);
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsStreaming(false);
    setProgram('');
    setStudent('');
    setResumeFile(null);
    setSelectedModel('gpt-3.5-turbo');
  }, []);

  return (
    <div className="w-auto h-auto border border-gray-600 flex flex-col justify-between p-4">
      {/* <h3 className="text-xl font-bold mb-4">College Essay Generator</h3> */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Student Name"
          value={student}
          onChange={(e) => setStudent(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded"
        />
      </div>
   
      <div className="mb-4">
        <input
          type="text"
          placeholder="Program"
          value={program}
          onChange={(e) => setProgram(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded"
        />
      </div>
      <div className="mb-4">
        <input
          type="file"
          accept=".txt,.pdf,.doc,.docx"
          onChange={(e) => setResumeFile(e.target.files[0])}
          className="w-full p-2 border border-gray-300 rounded"
        />
      </div>
      <div className="mb-4">
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded"
        >
          {models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>
      
      <div className="overflow-y-auto max-h-96 mb-4">
        {messages.map((message, index) => (
          <div key={index} className="mb-2 p-2 rounded bg-sky-500/100 shadow-lg shadow-sky-500/50">
            {message.text}
          </div>
        ))}
      </div>
      
      {pdfContent && (
        <div className="mb-4">
          <h4 className="text-lg font-semibold mb-2">Generated PDF:</h4>
          <iframe
            src={`data:application/pdf;base64,${pdfContent}`}
            width="100%"
            height="500px"
            title="Generated Essay PDF"
          />
        </div>
      )}
      
      <div className="flex space-x-2">
        <button
          onClick={startStreaming}
          disabled={isStreaming}
          className={`px-4 py-2 rounded-full ${
            isStreaming ? "bg-gray-400 cursor-not-allowed" : "bg-sky-500 text-white"
          }`}
        >
          {isStreaming ? "Generating Essay..." : "Start Essay Generation"}
        </button>
        <button 
          onClick={handleClear}
          className="px-4 py-2 bg-red-500 text-white rounded-full"
        >
          Clear
        </button>
      </div>
      
      {error && (
        <div className="mt-4">
          <p className="text-red-500">{error}</p>
        </div>
      )}
    </div>
  );
};

export default CollegeEssayStreamer;