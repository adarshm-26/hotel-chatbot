import React from 'react';
import 'bootstrap/dist/css/bootstrap.css';
import { post } from './Utils';
import { Container, Nav, Button, FormControl, InputGroup } from 'react-bootstrap';

export const Chatbot = () => {
  const [active, setActive] = React.useState(false);
  const [messages, setMessages] = React.useState([]);

  const addMessage = React.useCallback((message) => {
    let oldMsgs = [...messages];
    console.log(messages);
    oldMsgs.push(message);
    console.log(oldMsgs);
    setMessages(oldMsgs);
  }, [messages]);

  const sendMessage = React.useCallback(async (message) => {
    let results = await post(
      '/webhooks/rest/webhook', {
        sender: 'user',
        message: message
      });
    return results;
  }, []);
  
  if (!active) {
    return <Button 
    className='chatbot-button'
    onClick={() => setActive(true)}
    variant='success'>
      Let's chat
    </Button>;
  }
  
  return <div className='chatbot-chatbox'>
    <MessageArea messages={messages}/>
    <Textbox onSend={ async (message) => {
      addMessage(message);
      let results = await sendMessage(message);
      results.forEach(result => addMessage(result.text));
    }}/>
  </div>;
}

const MessageArea = ({ messages }) => {
  return <div className='chatbot-msg-area'>
    {
      messages.map((value, index) => 
        <div key={index} 
        className='chatbot-msg-pill'>
          {value}
        </div>
      )
    }
  </div>
}

const Textbox = ({ onSend }) => {
  const [message, setMessage] = React.useState('');

  return <div className='chatbot-textbox'>
    <InputGroup>
      <FormControl
        placeholder='Write something !'
        value={message}
        onChange={(e) => {
          e.preventDefault();
          setMessage(e.target.value);
        }}
        aria-label='Write messages'
        aria-describedby='basic-addon2'
      />
      <InputGroup.Append>
        <Button 
        variant='outline-success'
        onClick={() => onSend(message)}>Send</Button>
      </InputGroup.Append>
    </InputGroup>
  </div>
}
