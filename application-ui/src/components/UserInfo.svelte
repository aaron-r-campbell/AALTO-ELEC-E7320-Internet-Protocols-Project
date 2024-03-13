<script>
    import { onMount } from "svelte";
    import { state } from "../stores/state_store";

    export let user = {};

    onMount(async () => {
        try {
            user.username = $state.username;
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
