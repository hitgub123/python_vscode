import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div>
      <h1>欢迎来到小说/漫画网站</h1>
      <nav>
        <Link to="/login">登录</Link> | <Link to="/register">注册</Link>
      </nav>
    </div>
  );
}

export default Home;
