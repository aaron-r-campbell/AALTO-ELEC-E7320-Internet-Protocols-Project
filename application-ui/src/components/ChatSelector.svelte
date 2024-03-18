<script>
    import { onMount } from "svelte";
    import { state } from "../stores/state_store.js";

    let rooms = [];
    export let handleRoomSelection;
    export let selectedRoomID;

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
                        if (!rooms.some((r) => r.room_id === selectedRoomID)) {
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
</script>

<ul id="chats-list">
    {#each rooms as room}
        <li>
            <button
                type="button"
                on:click={() => handleRoomSelection(room.room_id)}
            >
                {room.room_name}
            </button>
        </li>
    {/each}
</ul>

<style>
    #chats-list {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    #chats-list li {
        margin-bottom: 10px;
        padding: 8px;
        background-color: #34495e; /* Chat item background color */
        color: white;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    #chats-list li:hover {
        background-color: #2c3e50; /* Hover state background color */
    }
</style>
