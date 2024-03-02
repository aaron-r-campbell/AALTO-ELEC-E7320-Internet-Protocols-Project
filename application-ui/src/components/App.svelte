<script>
    import axios from "axios";
    import { onMount } from "svelte";

    let username = "";
    let chats = [];

    const get_username = async () => {
        const response = await axios.get(
            "/api/whoami",
            {},
            { withCredentials: true },
        );
        username = response.data.username;
    };

    onMount(async () => {
        get_username();
    });
</script>

<h1>Welcome {username}!</h1>
<div style="display:flex;">
    <div style="width: 20vw; background-color: lightgray;">
        <h1>Chats:</h1>
        {#each chats as chat}
            <p>{chat.name}</p>
        {/each}
    </div>
    <div style="width: 80vw;"></div>
</div>
