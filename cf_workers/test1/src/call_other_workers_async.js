addEventListener('fetch', event => {
	event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
	// Worker1 的主要逻辑
	const result = 'Worker1 已完成处理';

	// 在结束时调用 Worker2
	const worker2Url = 'https://worker2.example.workers.dev';
	fetch(worker2Url, {
		method: 'POST', // 或 GET，根据需要
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ message: '来自 Worker1 的调用' })
	}).catch(err => console.error('调用 Worker2 失败:', err)); // 异步调用，不等待结果

	// 直接返回 Worker1 的响应
	return new Response(result, { status: 200 });
}