<script>
    import Chat from "../components/Chat.svelte";

    import { goto } from "$app/navigation";
    import axios from "axios";
    import { onMount } from "svelte";

    let isLoading = true;
    let username = "";
    let chats = [];

    const check_auth = async () => {
        console.log("auth is ", axios.defaults.headers.common["Authorization"]);
        if (!axios.defaults.headers.common["Authorization"]) {
            goto("/login");
            return;
        }
        isLoading = false;
        const response = await axios.get(
            "/api/whoami",
            {},
            { withCredentials: true },
        );
        username = response.data.username;
    };

    onMount(async () => {
        check_auth();
    });
</script>

{#if isLoading}
    <div class="spinner"></div>
{:else}
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
{/if}

<style>
    .spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-top: 4px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: auto auto;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
</style>
