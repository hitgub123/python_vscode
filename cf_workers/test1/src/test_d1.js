// src/index.ts
var index_default = {
	async fetch(request, env) {

		const DB = env.D1_DB;

		// const { results } = await DB.prepare("SELECT * FROM users").all();
		// return new Response(JSON.stringify(results), {
		// 	headers: { "Content-Type": "application/json" },
		// });

		const id = 4;
		const name = 'ccccc';
		const email = 'cc@ccccccc.com';
		// await DB.prepare("INSERT INTO users (name, email) VALUES (?, ?)")
		// 	.bind(name, email)
		// 	.run();

		// await DB.prepare("UPDATE users SET name = ?, email = ? WHERE id = ?")
		// 	.bind(name, email, id)
		// 	.run();

		// await DB.prepare("DELETE FROM users WHERE id = ?").bind(id).run();

		const statements = [
			DB.prepare("INSERT INTO users (name, email) VALUES (?, ?)").bind('d', 'dd@ddd.com'),
			DB.prepare("INSERT INTO users (name, email) VALUES (?, ?)").bind('e', 'ee@eee.com'),
		]
		await DB.batch(statements);

		return new Response(JSON.stringify({ success: true }));
	}
};
export {
	index_default as default
};