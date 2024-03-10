<script>
    import { onMount } from "svelte";
    import { state } from "../stores/state_store.js";
    import ChatSelector from "../components/ChatSelector.svelte";
    import UserInfo from "../components/UserInfo.svelte";
    import Chat from "../components/Chat.svelte";
    import ChatInput from "../components/ChatInput.svelte";
    import PingResult from "../components/PingResult.svelte";
    import PeerInfo from "../components/PeerInfo.svelte";
    import CreateRoom from "../components/CreateRoom.svelte";

    let user = {};
    let selectedRoomID = null;

    function handleRoomSelection(roomID) {
        console.log("CHANGING TO ROOM", roomID);
        selectedRoomID = roomID;
    }
    console.log("hello");
</script>

<div id="app">
    <div id="sidebar">
        <UserInfo bind:user />
        <CreateRoom />
        <ChatSelector {handleRoomSelection} />
        <PingResult />
        <PeerInfo />
    </div>
    <div id="chats">
        <div id="chat-container">
            {#if selectedRoomID !== null}
                <Chat {user} {selectedRoomID} />
            {/if}
        </div>
        <ChatInput {user} {selectedRoomID} />
    </div>
</div>

<style>
    #app {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        display: flex;
        height: 100vh;
    }
    #chats {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #ecf0f1; /* Light background color */
    }

    #chat-container {
        flex: 1; /* Grow to fill remaining space */
    }

    #sidebar {
        width: 250px;
        background-color: #2c3e50; /* Dark background color */
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        color: white; /* Text color */
    }
</style>
