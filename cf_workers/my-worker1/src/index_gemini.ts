export default {
	async fetch(request: Request, env: any): Promise<Response> {
		// 打印 env 变量以调试
		// console.log('Environment variables:', JSON.stringify(Object.keys(env)));

		// 验证环境变量
		// if (!env.GEMINI_API_KEY) {
		// 	return new Response(JSON.stringify({ error: 'Configuration Error', message: 'GEMINI_API_KEY is not set' }), {
		// 		status: 500,
		// 		headers: { 'Content-Type': 'application/json' },
		// 	});
		// }
		const mpdel_name = 'gemini-2.5-flash-lite';
		const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${mpdel_name}:generateContent?key=${env.GEMINI_API_KEY2}`;

		try {
			// 从 URL 获取问题
			const url = new URL(request.url);
			const question = url.searchParams.get('question') || '我是阿黄，你是谁？';

			// 调用 Gemini API
			const response = await fetch(GEMINI_API_URL, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					contents: [{ parts: [{ text: question }] }],
				}),
			});

			if (!response.ok) {
				const errorData = await response.json();
				return new Response(JSON.stringify(errorData), {
					status: response.status,
					headers: { 'Content-Type': 'application/json' },
				});
			}

			const json:any = await response.json();
			const data = json.candidates[0].content.parts; // 移除不必要的 await
			return new Response(JSON.stringify(data), {
				headers: { 'Content-Type': 'application/json' },
			});
		} catch (error: any) {
			return new Response(JSON.stringify({ error: 'Internal Server Error', message: error.message }), {
				status: 500,
				headers: { 'Content-Type': 'application/json' },
			});
		}
	},
};

// Define environment variables interface
interface Env {
	DISCORD_WEBHOOK_URL: string;
	GEMINI_API_KEY: string;
}
