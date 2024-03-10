<script>
    import Chat from "./Chat.svelte";
    import ChatInput from "./ChatInput.svelte";
    
    export let user;
    export let selectedRoomID;
</script>

<div id="chats">
    {#if selectedRoomID !== null}
        <Chat {user} {selectedRoomID} />
    {/if}
    <ChatInput {user} {selectedRoomID} />
</div>


<style>
    #chats {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #ecf0f1; /* Light background color */
    }
</style>
