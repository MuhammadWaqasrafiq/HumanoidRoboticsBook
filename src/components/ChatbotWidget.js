import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Button, List, ListItem, ListItemText, Paper, Typography, Fab, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

function ChatbotWidget() {
  if (!ExecutionEnvironment.canUseDOM) {
    return null; // Don't render on the server
  }

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [selectedText, setSelectedText] = useState('');
  const [buttonPosition, setButtonPosition] = useState({ top: 0, left: 0, display: 'none' });
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    if (ExecutionEnvironment.canUseDOM) {
      const { v4: uuidv4 } = require('uuid');
      setSessionId(uuidv4());

      const handleMouseUp = () => {
        const selection = window.getSelection();
        if (selection.toString().length > 0) {
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();
          setSelectedText(selection.toString());
          setButtonPosition({
            top: rect.bottom + window.scrollY,
            left: rect.left + window.scrollX + rect.width / 2,
            display: 'block',
          });
        } else {
          setButtonPosition({ display: 'none' });
        }
      };

      document.addEventListener('mouseup', handleMouseUp);
      return () => document.removeEventListener('mouseup', handleMouseUp);
    }
  }, []);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { sender: 'user', text: input };
      setMessages((prev) => [...prev, userMessage]);
      setInput('');

      try {
        const response = await axios.post('/api/chat', { 
          message: input,
          session_id: sessionId,
          context: selectedText
        });
        setSelectedText(''); // Clear selected text after sending
        const botMessage = { sender: 'bot', text: response.data.answer };
        setMessages((prev) => [...prev, botMessage]);
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage = { sender: 'bot', text: 'Sorry, failed to connect.' };
        setMessages((prev) => [...prev, errorMessage]);
      }
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') handleSend();
  };

  const handleAskAboutSelection = () => {
    setIsOpen(true);
    setInput(`What does this mean: "${selectedText}"?`);
    setSelectedText('');
    setButtonPosition({ display: 'none' });
  };

  if (!isOpen) {
    return (
      <>
        <Fab
          color="primary"
          aria-label="chat"
          onClick={() => setIsOpen(true)}
          sx={{ position: 'fixed', bottom: 24, right: 24, zIndex: 1000 }}
        >
          <ChatIcon />
        </Fab>
        <Fab
          color="secondary"
          aria-label="ask"
          onClick={handleAskAboutSelection}
          sx={{
            position: 'absolute',
            top: buttonPosition.top,
            left: buttonPosition.left,
            display: buttonPosition.display,
            zIndex: 1001,
            transform: 'translate(-50%, -120%)',
          }}
          size="small"
        >
          <ChatIcon fontSize="small" />
        </Fab>
      </>
    );
  }

  return (
    <Paper
      elevation={8}
      sx={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        width: 370,
        height: 500,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        borderRadius: '16px',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          p: 2,
          backgroundColor: 'primary.main',
          color: 'white',
          borderTopLeftRadius: '16px',
          borderTopRightRadius: '16px',
        }}
      >
        <Typography variant="h6">RAG Chatbot</Typography>
        <IconButton onClick={() => setIsOpen(false)} sx={{ color: 'white' }}>
          <CloseIcon />
        </IconButton>
      </Box>
      <List sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {messages.map((msg, index) => (
          <ListItem key={index} sx={{ justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
            <Box
              sx={{
                bgcolor: msg.sender === 'user' ? 'primary.light' : 'grey.200',
                color: msg.sender === 'user' ? 'primary.contrastText' : 'black',
                p: 1.5,
                borderRadius: '10px',
                maxWidth: '80%',
              }}
            >
              <ListItemText primary={msg.text} />
            </Box>
          </ListItem>
        ))}
        <div ref={endOfMessagesRef} />
      </List>
      <Box sx={{ p: 2, display: 'flex', borderTop: '1px solid #ddd' }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <Button variant="contained" onClick={handleSend} sx={{ ml: 1 }}><SendIcon /></Button>
      </Box>
    </Paper>
  );
}

export default ChatbotWidget;
