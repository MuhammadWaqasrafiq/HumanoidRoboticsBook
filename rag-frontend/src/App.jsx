import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Container,
  Paper,
  Typography,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { sender: 'user', text: input };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInput('');

      try {
        const response = await axios.post('http://127.0.0.1:8000/api/chat', {
          message: input,
        });
        
        // Assuming the backend returns a JSON with a 'response' field
        const botMessage = { sender: 'bot', text: response.data.response };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage = { sender: 'bot', text: 'Sorry, I am having trouble connecting to the server.' };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
      }
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <Container maxWidth="md" sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" component="h1" align="center" gutterBottom sx={{ mt: 2, color: 'primary.main' }}>
        RAG Chatbot
      </Typography>
      <Paper elevation={3} sx={{ flexGrow: 1, overflow: 'auto', p: 2, display: 'flex', flexDirection: 'column' }}>
        <List sx={{ flexGrow: 1 }}>
          {messages.map((msg, index) => (
            <ListItem key={index} sx={{ justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <Box
                sx={{
                  bgcolor: msg.sender === 'user' ? 'primary.main' : 'grey.300',
                  color: msg.sender === 'user' ? 'primary.contrastText' : 'black',
                  p: 1.5,
                  borderRadius: '10px',
                  maxWidth: '70%',
                }}
              >
                <ListItemText primary={msg.text} />
              </Box>
            </ListItem>
          ))}
          <div ref={endOfMessagesRef} />
        </List>
      </Paper>
      <Box sx={{ p: 2, display: 'flex' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSend}
          sx={{ ml: 1 }}
          endIcon={<SendIcon />}
        >
          Send
        </Button>
      </Box>
    </Container>
  );
}

export default App;