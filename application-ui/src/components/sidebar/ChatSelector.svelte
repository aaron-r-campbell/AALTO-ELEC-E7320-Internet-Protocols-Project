<script>
    import { onMount } from "svelte";
    import { state } from "/app/src/stores/state_store.js";
    import CreateRoom from "/app/src/components/sidebar/CreateRoom.svelte";

    let rooms = [];
    export let handleRoomSelection;
    export let selectedRoom;
    let searchValue = "";

    onMount(async () => {
        try {
            console.log("getting user rooms");
            // rooms = await getUserRooms();
            $state.socket.emit("get_user_rooms");

            // We keep the listener as when a user is invited to a room, the same message is sent or when a user is invited to a room
            $state.socket.on("return_user_rooms", (payload) => {
                if (payload.successful) {
                    console.log("GOT RETURN USER ROOMS:", payload.payload);
                    rooms = payload.payload;
                } else {
                    console.error(
                        "Did not get new user rooms:",
                        payload.description,
                    );
                }
            });
            console.log("Fetched rooms:", rooms);

            $state.socket.on(
                "remove_room_response",
                (successful, description, room_id) => {
                    if (successful) {
                        console.log("Got 'Remove room' with room_id", room_id);
                        rooms = rooms.filter((x) => x.room_id !== room_id);

                        // If the current room doesn't exist anymore, close the chat
                        if (!rooms.some((r) => r === selectedRoom)) {
                            handleRoomSelection(null);
                        }
                    } else {
                        console.error(description);
                    }
                },
            );
        } catch (error) {
            console.error("Error fetching user chats:", error);
        }
    });

    function openCreateRoomModal() {
        document.getElementById("createRoomModal").style.display = "block";
    }

    function closeCreateRoomModal() {
        document.getElementById("createRoomModal").style.display = "none";
    }
</script>

<h2>Chatrooms</h2>
<div style="display: flex; gap: 16px;">
    <input
        type="text"
        placeholder="Search"
        class="fw"
        style="margin: 0;"
        bind:value={searchValue}
    />
    <button
        type="button"
        class="fw"
        style="height: 100%;"
        on:click={openCreateRoomModal}>Create Room</button
    >
</div>
<ul id="chats-list">
    {#each rooms.filter((room) => searchValue == "" || room.room_name
                .toLowerCase()
                .includes(searchValue.toLowerCase())) as room}
        <li>
            <button
                type="button"
                class="fw"
                on:click={handleRoomSelection(room)}
            >
                {room.room_name}
            </button>
        </li>
    {/each}
    <!-- <li><CreateRoom /></li> -->
</ul>

<!-- Modal for creating a chat room -->
<div
    id="createRoomModal"
    class="card"
    style="display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); color: var(--text-color);"
>
    <h2>Create Chatroom</h2>
    <form>
        <label for="roomNameInput">Room name:</label>
        <input type="text" id="roomNameInput" placeholder="Enter room name" />
        <div style="display:flex; justify-content: flex-end; gap: 16px;">
            <button
                type="button"
                class="red-button"
                on:click={closeCreateRoomModal}>Cancel</button
            >
            <button type="submit">Create</button>
        </div>
    </form>
</div>

<style>
    #chats-list {
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 16px;
        list-style: none;
    }

    #chats-list li {
        cursor: pointer;
    }

    #chats-list li button {
        color: var(--text-color);
        background-color: var(--background-color);
    }

    #chats-list li button:hover {
        background-color: var(--border-color);
    }

    .red-button {
        background-color: var(--primary-red);
    }
    .red-button:hover {
        background-color: var(--primary-hover-red);
    }
</style>
