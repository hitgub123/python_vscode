import { createJWT, verifyPassword } from '../utils/auth.js';

export async function onRequest(context) {
  // context 对象包含了请求、环境绑定 (DB, R2, KV) 等所有信息
  const { request, env } = context;
  const url = new URL(request.url);

  // 简单的路由逻辑
  if (url.pathname === '/api/register' && request.method === 'POST') {
    return await handleRegister(context);
  }

  if (url.pathname === '/api/login' && request.method === 'POST') {
    return await handleLogin(context);
  }

  // 其他路由...

  return new Response('Not Found', { status: 404 });
}

// 用户注册处理函数
async function handleRegister({ request, env }) {
  try {
    const { email, password } = await request.json();

    // 1. 数据校验
    if (!email || !password || password.length < 8) {
      return new Response(JSON.stringify({ success: false, message: '邮箱或密码无效 (密码至少8位)' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // 2. 密码加密
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const passwordKey = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(password),
      { name: 'PBKDF2' },
      false,
      ['deriveBits']
    );
    const hashedPassword = await crypto.subtle.deriveBits(
      {
        name: 'PBKDF2',
        salt: salt,
        iterations: 100000,
        hash: 'SHA-256',
      },
      passwordKey,
      256
    );

    // 将 salt 和哈希后的密码组合存储
    const password_hash = `${Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('')}:${Array.from(new Uint8Array(hashedPassword)).map(b => b.toString(16).padStart(2, '0')).join('')}`;

    // 3. 存入数据库
    const ps = env.DB.prepare('INSERT INTO Users (email, password_hash) VALUES (?, ?)');
    await ps.bind(email, password_hash).run();

    return new Response(JSON.stringify({ success: true, message: '注册成功' }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    // 捕获唯一的 email 约束冲突
    if (error.message.includes('UNIQUE constraint failed')) {
      return new Response(JSON.stringify({ success: false, message: '该邮箱已被注册' }), {
        status: 409, // Conflict
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return new Response(JSON.stringify({ success: false, message: '注册失败', error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

async function handleLogin({ request, env }) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return new Response(JSON.stringify({ success: false, message: '需要邮箱和密码' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // 1. 从数据库查找用户
    const ps = env.DB.prepare('SELECT id, email, password_hash FROM Users WHERE email = ?');
    const user = await ps.bind(email).first();

    if (!user) {
      return new Response(JSON.stringify({ success: false, message: '用户不存在或密码错误' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // 2. 验证密码
    const passwordIsValid = await verifyPassword(password, user.password_hash);

    if (!passwordIsValid) {
      return new Response(JSON.stringify({ success: false, message: '用户不存在或密码错误' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // 3. 生成 JWT
    const jwtSecret = await env.SETTINGS_KV.get('JWT_SECRET');
    const token = await createJWT({ id: user.id, email: user.email }, jwtSecret);

    return new Response(JSON.stringify({ success: true, token }), {
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    return new Response(JSON.stringify({ success: false, message: '登录失败', error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
