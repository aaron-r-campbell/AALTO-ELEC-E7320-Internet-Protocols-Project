<script>
    import { onMount } from "svelte";
    import { state } from "../stores/state_store.js";

    let rooms = [];
    export let handleRoomSelection;

    onMount(async () => {
        try {
            console.log("getting user rooms");
            // rooms = await getUserRooms();
            $state.socket.emit("get_user_rooms");

            // We keep the listener as when a user is invited to a room, the same message is sent or when a user is invited to a room
            $state.socket.on("return_user_rooms", (new_rooms) => {
                console.log("GOT RETURN USER ROOMS:", new_rooms);
                rooms = new_rooms;
            });
            console.log("Fetched rooms:", rooms);
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
