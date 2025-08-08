import React, { useState } from 'react';
import authService from '../services/authService';

function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const response = await authService.register({ email, password });
      setMessage(response.data.message);
    } catch (error) {
      setMessage(error.response.data.message);
    }
  };

  return (
    <div>
      <h2>注册</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="邮箱" required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="密码 (至少8位)" required />
        <button type="submit">注册</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Register;
