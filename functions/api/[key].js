export async function onRequestGet(context) {
    // 1. Extract the requested image filename (e.g., UUID.jpg) from the URL
    const imageKey = context.params.key;

    // 2. Check if the R2 binding exists
    if (!context.env.PHOTOS) {
        return new Response("R2 Bucket binding 'PHOTOS' missing", { status: 500 });
    }

    try {
        // 3. Fetch object from R2 Bucket
        const object = await context.env.PHOTOS.get(imageKey);

        if (!object) {
            return new Response("Photo Not Found", { status: 404 });
        }

        // 4. Return image with proper headers and caching
        const headers = new Headers();
        object.writeHttpMetadata(headers);
        headers.set("etag", object.httpEtag);
        headers.set("content-type", "image/jpeg");
        headers.set("cache-control", "public, max-age=86400"); // Cache at edge for 24 hours

        return new Response(object.body, { headers });

    } catch (err) {
        return new Response("Error retrieving image", { status: 500 });
    }
}