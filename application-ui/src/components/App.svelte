<script>
    import Sidebar from "/app/src/components/sidebar/Sidebar.svelte";
    import ChatRoom from "/app/src/components/chat/ChatRoom.svelte";
    import File from "/app/src/components/files/File.svelte";

    const navOptions = [
        { page: "messages", component: "ChatRoom" },
        { page: "files", component: "File" },
    ];

    let selectedComponent = "ChatRoom",
        user = {},
        selectedRoom = null,
        hideSidebar = true;
    const isMobile = window.matchMedia("(max-width: 767px)").matches;

    function handleRoomSelection(room) {
        console.log("CHANGING TO ROOM", room);
        selectedRoom = room;
    }

    function changeComponent(component) {
        console.log("CHANGING TO VIEW", component);
        selectedComponent = component;
    }
</script>

<Sidebar {handleRoomSelection} {selectedRoom} {isMobile} />
<div id="page">
    <div class="navbar">
        {#each navOptions as option, i}
            <button
                class={option.component === selectedComponent ? "" : "inactive"}
                on:click={() => changeComponent(option.component)}
                >{option.page}</button
            >
        {/each}
    </div>
    <div id="page-content">
        {#if selectedRoom === null}
            <div class="centerInner">
                <h1 style="color: #999;">
                    Select a chatroom from the sidebar to begin.
                </h1>
            </div>
        {:else if selectedComponent === "ChatRoom"}
            <ChatRoom {user} {selectedRoom} />
        {:else if selectedComponent === "File"}
            <File {user} {selectedRoom} />
        {/if}
    </div>
</div>

<style>
    #page {
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
        width: 100%;
    }

    #page-content {
        height: 95%;
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background-color: var(--background-color);
    }

    .navbar {
        display: flex;
        gap: 8px;
        padding: 8px;
        padding-bottom: 0;
        background-color: #fff;
    }

    .navbar button {
        border-bottom-right-radius: 0;
        border-bottom-left-radius: 0;
    }

    .inactive {
        background-color: #2b2b2b;
    }

    .inactive:hover {
        background-color: #4b4b4b;
    }
</style>
