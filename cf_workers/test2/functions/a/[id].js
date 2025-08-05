export async function onRequest(context) {
    const { params, env } = context;
    const id = params.id;
    const bucket = env['BUCKET_'];
    const object = await bucket.get(`${id}.html`);
    // const object = await bucket.get('2.html');
    console.log(`id: ${id}`);
    console.log(`bucket: ${bucket}`);
    console.log(`object: ${object}`);
    if(object){
        return new Response(object.body, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    }
    return new Response(`article[${id}] not found`, { status: 404 });
}