<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import io from "socket.io-client";
    import { state } from "/app/src/stores/state_store.js";
    import App from "/app/src/components/App.svelte";
    import Spinner from "/app/src/components/Spinner.svelte";

    let isLoading = true;

    onMount(() => {
        if (!$state.token) {
            goto("/login");
        } else if (!$state.socket) {
            const socket = io("/");

            // Run on authenticate response
            socket.on("authenticate_ack", (data) => {
                console.log("Auth_ack received", data);
                if (data?.successful) {
                    console.log("Authentication successful");
                    state.set({ ...$state, socket });
                    isLoading = false;
                } else {
                    console.error("Socket error: ", data?.description);
                    reject(data?.description);
                }
            });

            socket.on("connect", () => {
                console.log("connection established");
                socket.emit("authenticate", $state.token);
            });
        } else {
            isLoading = false;
        }
    });
</script>

{#if isLoading}
    <div class="centerInner">
        <Spinner />
    </div>
{:else}
    <App />
{/if}

<style global>
    @import "/app/public/style.css";
</style>
