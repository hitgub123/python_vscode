import React, { useState } from 'react';
import authService from '../services/authService';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const response = await authService.login({ email, password });
      // 登录成功，保存 token
      localStorage.setItem('token', response.data.token);
      setMessage('登录成功!');
      // 跳转到首页或用户中心
      window.location.href = '/';
    } catch (error) {
      setMessage(error.response.data.message);
    }
  };

  return (
    <div>
      <h2>登录</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="邮箱" required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="密码" required />
        <button type="submit">登录</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Login;
