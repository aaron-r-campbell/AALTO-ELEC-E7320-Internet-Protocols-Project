<script>
    import axios from "axios";
    import { state } from "../stores/state_store";
    import Chat from "../components/Chat.svelte";
    export let data;
    const { chatId } = data;

    onMount(async () => {
        console.log("auth is ", axios.defaults.headers.common["Authorization"]);
        if (!axios.defaults.headers.common["Authorization"]) {
            goto("/login");
            return;
        }
    });
</script>

<h1>{chatId}</h1>
<Chat bind:current_user={$state.username} />
