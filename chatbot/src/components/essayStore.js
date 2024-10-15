// essayStore.js
import { create } from 'zustand';

const useEssayStore = create((set) => ({
  program: '',
  student: '',
  college: '',
  resumeFile: null,
  selectedModel: 'o1-mini',
  messages: [],
  isStreaming: false,
  error: null,
  pdfContent: null,

  setProgram: (program) => set({ program }),
  setStudent: (student) => set({ student }),
  setCollege: (college) => set({ college }),
  setResumeFile: (resumeFile) => set({ resumeFile }),
  setSelectedModel: (selectedModel) => set({ selectedModel }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  setError: (error) => set({ error }),
  setPdfContent: (pdfContent) => set({ pdfContent }),

  clearAll: () => set({
    program: '',
    student: '',
    college: '',
    resumeFile: null,
    selectedModel: 'o1-mini',
    messages: [],
    isStreaming: false,
    error: null,
    pdfContent: null,
  }),
}));

export default useEssayStore;



