import './App.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ChatBot from "./components/Chatbot"
import About from "./pages/About";
import NotFound from "./pages/NotFound";
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import CollegeEssayStreamer from "./components/CollegeEssayStreamer";


function App() {
  return (
    <Router>
      <Navbar />
        <main className="container mx-auto px-3 pb-12">
          <Routes>
            <Route path="/" element={<CollegeEssayStreamer />} />
            <Route path="/essay" element={<CollegeEssayStreamer />} />
            <Route path="/chat" element={<ChatBot />} />
            <Route path="/notfound" element={<NotFound />} />
            <Route path="/about" element={<About />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
    </Router>
  );
}

export default App;
