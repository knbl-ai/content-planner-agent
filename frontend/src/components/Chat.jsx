import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [guideline, setGuideline] = useState('');
  const [showGuideline, setShowGuideline] = useState(false);
  
  const messagesEndRef = useRef(null);

  // Generate a session ID when the component mounts
  useEffect(() => {
    const newSessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
    
    // Add welcome message
    setMessages([
      { 
        role: 'assistant', 
        content: 'Hi! I\'ll help you create content guidelines for social media. Tell me about your needs.'
      }
    ]);
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: input,
        session_id: sessionId
      });

      // Add assistant response to chat
      setMessages(prev => [
        ...prev, 
        { role: 'assistant', content: response.data.response }
      ]);
      
      // Extract guideline from response
      const pattern = /GUIDELINE UPDATE:(.*?)END GUIDELINE UPDATE/s;
      const match = response.data.response.match(pattern);
      
      if (match && match[1]) {
        setGuideline(prev => {
          const newUpdate = match[1].trim();
          return prev ? `${prev}\n\n${newUpdate}` : newUpdate;
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: 'Sorry, there was an error processing your request.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const saveGuideline = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/save', {
        guideline,
        session_id: sessionId
      });

      if (response.data.success) {
        setMessages(prev => [
          ...prev, 
          { 
            role: 'assistant', 
            content: 'Guideline saved successfully.'
          }
        ]);
      } else {
        setMessages(prev => [
          ...prev, 
          { 
            role: 'assistant', 
            content: 'Error saving guideline.'
          }
        ]);
      }
    } catch (error) {
      console.error('Error saving guideline:', error);
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: 'Error saving guideline.'
        }
      ]);
    }
  };

  const toggleGuideline = () => {
    setShowGuideline(!showGuideline);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button onClick={toggleGuideline}>
          {showGuideline ? 'Hide Guideline' : 'Show Guideline'}
        </button>
      </div>

      {showGuideline && (
        <div className="guideline-panel">
          <div className="guideline-content">
            <ReactMarkdown>{guideline || 'No guideline yet.'}</ReactMarkdown>
          </div>
          <button onClick={saveGuideline}>Save</button>
        </div>
      )}

      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content loading">Thinking</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message..."
          disabled={isLoading}
          rows="1"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat; 