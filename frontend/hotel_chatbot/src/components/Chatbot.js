import React from 'react';
import 'bootstrap/dist/css/bootstrap.css';
import { post } from './Utils';
import { Button, FormControl, InputGroup, ButtonGroup } from 'react-bootstrap';

export const Chatbot = () => {
  const [active, setActive] = React.useState(false);
  const [messages, setMessages] = React.useState([]);

  const addMessage = React.useCallback(message => {
    if (message.text.trim() === '')
      return;
    setMessages(oldMsgs => [
      message,
      ...oldMsgs
    ]);
  }, []);

  const sendMessage = React.useCallback(
    async (message, quiet = false, command = '') => {
      addMessage({
        sender: 'user',
        text: message
      });
      let results = await post(
        '/webhooks/rest/webhook', {
          sender: 'user',
          message: quiet ? command : message
        });
      results.forEach(result => addMessage({
        sender: 'bot',
        ...result
      }));
  }, [addMessage]);
  
  if (!active) {
    return <Button 
    className='chatbot-button'
    onClick={() => setActive(true)}
    variant='success'>
      Let's chat
    </Button>;
  }
  
  return <div className='chatbot-chatbox'>
    <TitleBar title='Hotel Chatbot' 
      onClose={() => setActive(false)}
      onReset={() => {
        sendMessage('/restart');
        setMessages([]);
      }}/>
    <MessageArea messages={messages} onSend={sendMessage} />
    <Textbox onSend={sendMessage}/>
  </div>;
}

const TitleBar = ({ title, onClose, onReset }) => {
  return <div className='chatbot-titlebar'>
    <div style={{ margin: '10px' }}>{title}</div>
    <div style={{ flex: 1 }}></div>
    <div>
      <Button className='chatbot-button-special'
        variant='outline-success'
        size='sm'
        onClick={onReset}>
        Reset
      </Button>
      <Button className='chatbot-button-special'
        variant='outline-success'
        size='sm'
        onClick={onClose}>
        Close
      </Button>
    </div>
  </div>
}

const MessagePill = ({ text, sender }) => {
  return <div className='chatbot-msg-row'>
    {sender === 'user' ? 
      <div style={{ flex: 1 }}></div> : <></>}
    <div className={`chatbot-msg-pill-${sender}`}>
      {text}
    </div>
  </div>
}

const MessageArea = ({ messages, onSend }) => {
  console.log(messages[0]?.buttons);
  return <div className='chatbot-msg-area'>
  {/* Handle buttons feature */}
  { messages[0]?.buttons ?
    <ButtonGroup>
    { messages[0].buttons.map((button, index) => 
      <Button className='chatbot-button-special'
        variant='outline-success'
        size='sm'
        key={`button-${index}`}
        onClick={() => {
          // Send button payload instead
          onSend(button.title, true, button.payload);
        }}>{button.title}</Button>
    )}
    </ButtonGroup> : <></>
  }
  { messages.map((message, index) => 
      <MessagePill 
        key={`message-${index}`}
        text={message.text}
        sender={message.sender}/>
  )}
  </div>;
}

const Textbox = ({ onSend }) => {
  const [message, setMessage] = React.useState('');

  const send = React.useCallback((message) => {
    // Send message
    onSend(message);
    // Clear text box
    setMessage('');
  }, [onSend]);

  return <InputGroup>
    <FormControl className='chatbot-textbox'
      placeholder='Talk to our assistant'
      value={message}
      onChange={(e) => {
        e.preventDefault();
        setMessage(e.target.value);
      }}
      onKeyUp={(e) => {
        // Handle 'Enter' key press
        if (e.keyCode === 13) {
          e.preventDefault();
          send(message);
        }
      }}
      aria-label='Write messages'
      aria-describedby='basic-addon2'
    />
    <InputGroup.Append>
      <Button className='chatbot-button-send'
        variant='outline-success'
        size='sm'
        onClick={() => send(message)}>Send</Button>
    </InputGroup.Append>
  </InputGroup>;
}
