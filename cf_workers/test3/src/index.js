export default {
	async fetch(req) {
		const url = new URL(req.url)
		url.pathname = "/__scheduled";
		url.searchParams.append("cron", "* * * * *");
		return new Response(`To test the scheduled handler, ensure you have used the "--test-scheduled" then try running "curl ${url.href}".`);
	},

	async scheduled(event, env, ctx) {
		const DISCORD_WEBHOOK_URL = env.DISCORD_WEBHOOK_URL;
		// const DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1401434668598825011/I6PMKdx4qPZ7Yb6GlfG69zqGCSKcDntph1Fh7O4hqR1t_nX-HCDdiYPhr7uNbreNoV0u";
		const message = {
			content: "hello11",
			username: "Cloudflare bot1"
		};
			await fetch(DISCORD_WEBHOOK_URL, {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify(message)
			});
		console.log(`trigger fired at ${new Date()}}`);
	},
};
