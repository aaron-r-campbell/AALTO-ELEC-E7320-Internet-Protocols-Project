<script>
    import { goto } from "$app/navigation";
    import { onMount } from "svelte";
    import { state } from "../stores/state_store.js";
    import App from "../components/App.svelte";
    import Spinner from "../components/Spinner.svelte";

    onMount(() => {
        if (!$state.token) goto("/login");
    });
</script>

{#if !$state.token}
    <Spinner />
{:else}
    <App />
{/if}
