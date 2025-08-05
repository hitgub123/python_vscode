export default {
	async fetch(request: Request, env: any): Promise<Response> {
		const DISCORD_WEBHOOK_URL = env.DISCORD_WEBHOOK_URL;
		console.log(DISCORD_WEBHOOK_URL);
		console.log('env', env);
		// const DISCORD_WEBHOOK_URL =
		// 'https://discord.com/api/webhooks/1401434668598825011/I6PMKdx4qPZ7Yb6GlfG69zqGCSKcDntph1Fh7O4hqR1t_nX-HCDdiYPhr7uNbreNoV0u';

		const message = {
			content: 'Hello from Cloudflare Workers!',
			username: 'Cloudflare bot1',
		};

		try {
			const response = await fetch(DISCORD_WEBHOOK_URL, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(message),
			});

			if (!response.ok) {
				const errorData = await response.json();
				return new Response(JSON.stringify({ error: 'Failed to send to Discord', details: errorData }), {
					status: response.status,
					headers: { 'Content-Type': 'application/json' },
				});
			}

			return new Response('Message sent to Discord', {
				status: 200,
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

