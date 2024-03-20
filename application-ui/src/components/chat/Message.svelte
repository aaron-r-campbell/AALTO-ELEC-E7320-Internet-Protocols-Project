<script>
    import Timestamp from "/app/src/components/chat/Timestamp.svelte";

    export let current_user = "",
        sender = "",
        content = "",
        timestamp = "";
</script>

<div class="message-container">
    <div
        class="message {current_user === sender
            ? 'own-message'
            : 'other-message'}"
    >
        <p>{content}</p>
        <span class="timestamp"
            ><b>{sender}</b> <Timestamp time={timestamp} /></span
        >
    </div>
</div>

<style>
    .message-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        margin-bottom: 10px;
    }

    .message {
        max-width: 70%;
        padding: 10px;
        border-radius: 8px;
        word-wrap: break-word;
        background-color: #ecf0f1; /* Message background color */
    }

    .own-message {
        align-self: flex-end;
        background-color: #4caf50; /* Green color for own messages */
        color: white;
    }

    .other-message {
        align-self: flex-start;
        background-color: #fff; /* Grey color for other messages */
        color: black;
    }

    .timestamp {
        font-size: 12px;
        color: #666;
        margin-top: 5px;
    }
</style>
