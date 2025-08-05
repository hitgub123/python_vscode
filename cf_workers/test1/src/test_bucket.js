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
		const bucket = env['BUCKET_'];
		// const object = await bucket.put("1.txt", "Hello, R222!");
		const doc = `${params.id}.html`
		const object = await bucket.get(doc);
		console.log(`bucket: ${bucket}`);
		console.log(`doc: ${doc}`);
		console.log(`object: ${object}`);

		return new Response(object ? object.body : 'not found', { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
	},
};
