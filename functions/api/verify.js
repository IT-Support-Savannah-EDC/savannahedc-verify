// This function runs automatically whenever someone visits verify.savannahedc.com/api/verify?id=YOUR_UUID
export async function onRequestGet(context) {
    // 1. Get the 'id' parameter from the URL query string
    const { searchParams } = new URL(context.request.url);
    const staffUuid = searchParams.get('id');

    // 2. Check if an ID was actually provided
    if (!staffUuid) {
        return new Response(JSON.stringify({ found: false, error: "Missing ID" }), {
            status: 400,
            headers: { "Content-Type": "application/json" }
        });
    }

    try {
        // 3. Search the Cloudflare D1 database for the matching staff UUID
        // 'DB' refers to your Cloudflare D1 binding
        const statement = context.env.DB.prepare("SELECT * FROM staff_directory WHERE uuid = ?");
        const staff = await statement.bind(staffUuid).first();

        // 4. If no staff member matches that ID
        if (!staff) {
            return new Response(JSON.stringify({ found: false }), {
                status: 404,
                headers: { "Content-Type": "application/json" }
            });
        }

        // 5. Return the staff details as JSON
        return new Response(JSON.stringify({ found: true, staff: staff }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });

    } catch (error) {
        return new Response(JSON.stringify({ found: false, error: "Database error" }), {
            status: 500,
            headers: { "Content-Type": "application/json" }
        });
    }
}