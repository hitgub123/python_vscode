// src/index.ts
var index_default = {
	async fetch(request, env) {
		const DISCORD_WEBHOOK_URL = env.DISCORD_WEBHOOK_URL;
		const kv = env.KV_NAMESPACE1;
		// kv.put("c1", "hello");
		let v = await kv.get("d1");
		console.log(v);
		v=v?v:"not found";
		const message = {
			content: v,
			username: "Cloudflare bot1"
		};
		try {
			const response = await fetch(DISCORD_WEBHOOK_URL, {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify(message)
			});
			if (!response.ok) {
				const errorData = await response.json();
				return new Response(JSON.stringify({ error: "Failed to send to Discord", details: errorData }), {
					status: response.status,
					headers: { "Content-Type": "application/json" }
				});
			}
			return new Response("Message sent to Discord", {
				status: 200,
				headers: { "Content-Type": "application/json" }
			});
		} catch (error) {
			return new Response(JSON.stringify({ error: "Internal Server Error", message: error.message }), {
				status: 500,
				headers: { "Content-Type": "application/json" }
			});
		}
	}
};
export {
	index_default as default
};