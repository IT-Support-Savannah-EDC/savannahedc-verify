export async function onRequestGet(context) {
    const { searchParams } = new URL(context.request.url);
    const staffUuid = searchParams.get('id');

    if (!staffUuid) {
        return new Response(JSON.stringify({ found: false, error: "Missing ID" }), {
            status: 400,
            headers: { "Content-Type": "application/json" }
        });
    }

    try {
        // Check if DB binding exists
        if (!context.env.DB) {
            throw new Error("D1 Binding 'DB' is missing in Cloudflare Pages Settings.");
        }

        const statement = context.env.DB.prepare("SELECT * FROM staff_directory WHERE uuid = ?");
        const staff = await statement.bind(staffUuid).first();

        if (!staff) {
            return new Response(JSON.stringify({ found: false }), {
                status: 404,
                headers: { "Content-Type": "application/json" }
            });
        }

        return new Response(JSON.stringify({ found: true, staff: staff }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });

    } catch (error) {
        // Expose the exact error details for debugging
        return new Response(JSON.stringify({ 
            found: false, 
            error_message: error.message,
            error_type: error.name
        }), {
            status: 500,
            headers: { "Content-Type": "application/json" }
        });
    }
}