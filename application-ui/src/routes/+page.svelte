<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import io from "socket.io-client";
    import { state } from "../stores/state_store.js";
    import App from "../components/App.svelte";
    import Spinner from "../components/Spinner.svelte";

    let isLoading = true;

    onMount(() => {
        if (!$state.token) {
            goto("/login");
        } else if (!$state.socket) {
            const socket = io("http://localhost:7777");

            socket.on("connect", () => {
                socket.emit("authenticate", $state.token);

                socket.on("error_event", (error) => {
                    console.error("Socket error: ", error);
                    reject(error);
                });

                state.set({ ...$state, socket });
                isLoading = false;
            });
        } else {
            isLoading = false;
        }
    });
</script>

{#if isLoading}
    <Spinner />
{:else}
    <App />
{/if}
