<script>
    import { state } from "/app/src/stores/state_store.js";
    import Timestamp from "/app/src/components/chat/Timestamp.svelte";

    export let sender = "",
        content = "",
        timestamp = "";
</script>

<div class="card {sender == $state.username ? 'own-message' : 'other-message'}">
    <p>{content}</p>
    <div class="timestamp">
        <b>{sender}</b>
        <Timestamp time={timestamp} />
    </div>
</div>

<style>
    .own-message {
        align-self: flex-end;
        background-color: #4caf50;
        color: white;
    }

    .other-message {
        align-self: flex-start;
        background-color: white;
        color: black;
    }

    .timestamp {
        font-size: 12px;
        display: flex;
        gap: 8px;
        justify-content: flex-end;
    }
</style>
