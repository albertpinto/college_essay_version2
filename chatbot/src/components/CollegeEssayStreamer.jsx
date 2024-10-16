import React, { useRef, useCallback } from 'react';
import useEssayStore from './essayStore';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const InputField = ({ placeholder, value, onChange }) => (
  <input
    type="text"
    placeholder={placeholder}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    className="w-full p-2 border border-gray-300 rounded mb-4"
  />
);

const FileInput = ({ onChange }) => (
  <input
    type="file"
    accept=".txt,.pdf,.doc,.docx"
    onChange={(e) => onChange(e.target.files[0])}
    className="w-full p-2 border border-gray-300 rounded mb-4"
  />
);

const Select = ({ value, onChange, options, placeholder }) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value)}
    className="w-full p-2 border border-gray-300 rounded mb-4"
  >
    <option value="" disabled>{placeholder}</option>
    {options.map((option) => (
      <option key={option} value={option}>
        {option}
      </option>
    ))}
  </select>
);

const MessageDisplay = ({ messages }) => (
  <div className="overflow-y-auto max-h-96 mb-4">
    {messages.map((message, index) => (
      <div key={index} className="mb-2 p-2 rounded bg-sky-500/100 shadow-lg shadow-sky-500/50">
        {message.text}
      </div>
    ))}
  </div>
);

const PDFViewer = ({ content }) => (
  <div className="mb-4">
    <h4 className="text-lg font-semibold mb-2">Generated PDF:</h4>
    <iframe
      src={`data:application/pdf;base64,${content}`}
      width="100%"
      height="500px"
      title="Generated Essay PDF"
    />
  </div>
);

const Button = ({ onClick, disabled, children, className }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`px-4 py-2 rounded-full ${className}`}
  >
    {children}
  </button>
);

const CollegeEssayStreamer = () => {
  const eventSourceRef = useRef(null);
  const {
    program, setProgram,
    student, setStudent,
    college, setCollege,
    resumeFile, setResumeFile,
    selectedModel, setSelectedModel,
    messages, addMessage, setMessages,
    isStreaming, setIsStreaming,
    error, setError,
    pdfContent, setPdfContent,
    clearAll
  } = useEssayStore();

  const models = [
    'o1-preview', 'o1-mini', 'gpt-4o', 'claude-2.5', 'gpt-3.5-turbo', 
    'mistral-nemo', 'llama3','llama3.1','llama3.2', 'mistral', 'phi', 'falcon'
  ];

  const colleges = [
    'University of California', 'University of Texas', 'University of Illinois', 
    'Harvard University', 'Yale University', 'Brown University', 'Stanford University', 
    'Cornell University', 'Carnegie Mellon University', 'Princeton University', 
    'Columbia University', 'University of Pennsylvania', 'Dartmouth College'
  ];

  const startStreaming = useCallback(async () => {
    if (!program || !student || !college || !resumeFile || !selectedModel) {
      setError('Please fill in all fields, select a college, upload a resume, and select a model before starting.');
      return;
    }

    setIsStreaming(true);
    setMessages([]);
    setError(null);
    setPdfContent(null);

    const formData = new FormData();
    formData.append('file', resumeFile);
    
    try {
      const uploadResponse = await fetch(`${API_BASE_URL}/upload_resume`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Resume upload failed');
      }

      const uploadResult = await uploadResponse.json();
      const resumeFilePath = uploadResult.file_path;

      const params = new URLSearchParams({ 
        program, 
        student, 
        college,
        resumeFilePath,
        model: selectedModel
      }).toString();
      eventSourceRef.current = new EventSource(`${API_BASE_URL}/stream_college_essay?${params}`);

      eventSourceRef.current.onmessage = (event) => {
        const data = event.data.replace(/^data: /, '').trim();
        if (data.startsWith('PDF_CONTENT:')) {
          const base64Content = data.replace('PDF_CONTENT:', '');
          setPdfContent(base64Content);
        } else if (data) {
          addMessage({ text: data, type: 'bot' });
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
  }, [program, student, college, resumeFile, selectedModel, setIsStreaming, setMessages, setError, setPdfContent, addMessage]);

  const handleClear = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    clearAll();
  }, [clearAll]);

  return (
    <div className="w-auto h-auto border border-gray-600 flex flex-col justify-between p-4">
      <InputField placeholder="Student Name" value={student} onChange={setStudent} />
      <InputField placeholder="Program" value={program} onChange={setProgram} />
      <Select 
        value={college} 
        onChange={setCollege} 
        options={colleges} 
        placeholder="Select College"
      />
      <FileInput onChange={setResumeFile} />
      <Select 
        value={selectedModel} 
        onChange={setSelectedModel} 
        options={models}
        placeholder="Select Model"
      />
      
      <MessageDisplay messages={messages} />
      
      {pdfContent && <PDFViewer content={pdfContent} />}
      
      <div className="flex space-x-2">
        <Button
          onClick={startStreaming}
          disabled={isStreaming}
          className={isStreaming ? "bg-gray-400 cursor-not-allowed" : "bg-sky-500 text-white"}
        >
          {isStreaming ? "Generating Essay..." : "Start Essay Generation"}
        </Button>
        <Button onClick={handleClear} className="bg-red-500 text-white">
          Clear
        </Button>
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