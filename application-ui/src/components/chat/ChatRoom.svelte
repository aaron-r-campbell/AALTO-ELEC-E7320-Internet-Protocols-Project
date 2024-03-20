<script>
    import Chat from "/app/src/components/chat/Chat.svelte";
    import ChatInput from "/app/src/components/chat/ChatInput.svelte";
    
    export let user;
    export let selectedRoom;
</script>

<div id="chats">
    {#if selectedRoom.room_id !== null}
        <Chat {user} {selectedRoom} />
    {/if}
    <ChatInput {user} {selectedRoom} />
</div>


<style>
    #chats {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #ecf0f1; /* Light background color */
    }
</style>
