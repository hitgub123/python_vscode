export default {
	async fetch(request, env, ctx) {
		let params = {};
		if (request.method === 'GET') {
			const url = new URL(request.url); // Parse the URL
			url.searchParams.forEach((value, key) => {
				params[key] = value;
			})
		} else if (request.method === 'POST') {
			params = await request.json();
		}

		const worker2Url = 'https://my-worker1.hotococoalj.workers.dev/';
		const resp=await fetch(worker2Url, {
			method: 'POST', // 或 GET，根据需要
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ message: '来自 Worker1 的调用', params })
		})

		return new Response(JSON.stringify(params), { headers: { 'Content-Type': 'application/json' } });
	},
};
