<script>
    import axios from "axios";
    import { onMount } from "svelte";
    import { state } from "../stores/state_store";

    export let user = {};

    const get_username = () => {
        return new Promise(async (resolve, reject) => {
            try {
                const response = await axios.get("/api/whoami", {
                    withCredentials: true,
                });
                resolve(response.data.username);
            } catch (error) {
                reject(error);
            }
        });
    };

    onMount(async () => {
        try {
            user.username = await get_username();
        } catch (error) {
            console.error("Error fetching username:", error);
        }
    });
</script>

<div id="current-user-info">
    {#if user?.username}
        <h1>{user.username}</h1>
    {:else}
        <h1>Loading...</h1>
    {/if}
</div>
