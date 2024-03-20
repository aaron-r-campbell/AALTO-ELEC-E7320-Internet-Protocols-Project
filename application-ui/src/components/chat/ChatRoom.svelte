<script>
    import Chat from "/app/src/components/chat/Chat.svelte";
    import ChatInput from "/app/src/components/chat/ChatInput.svelte";
    import InviteUsers from "/app/src/components/chat/InviteUsers.svelte";
    import RemoveRoom from "/app/src/components/chat/RemoveRoom.svelte";

    export let user, selectedRoom;
</script>

<div
    style="display: flex; justify-content: space-between; align-items: center; padding: 0 16px;"
>
    <h2>{selectedRoom.room_name}</h2>
    <div style="display: flex; gap: 8px;">
        <InviteUsers {selectedRoom} />
        <RemoveRoom {selectedRoom} />
    </div>
</div>
<Chat {user} {selectedRoom} />
<ChatInput {user} {selectedRoom} />
