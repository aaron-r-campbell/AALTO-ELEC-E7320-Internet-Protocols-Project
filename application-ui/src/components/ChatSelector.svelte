<script>
    import { onMount } from "svelte";
    import { state } from "../stores/state_store.js";

    let rooms = [];
    export let handleRoomSelection;

    const getUserRooms = () => {
        return new Promise((resolve, reject) => {
            $state.socket.emit("get_user_rooms");

            $state.socket.on("return_user_rooms", (rooms) => {
                resolve(rooms);
            });
        });
    };

    onMount(async () => {
        try {
            console.log("getting user rooms");
            rooms = await getUserRooms();
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
