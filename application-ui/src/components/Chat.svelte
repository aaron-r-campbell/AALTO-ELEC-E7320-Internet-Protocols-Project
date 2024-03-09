<script>
    import { state } from "../stores/state_store.js";
    import Message from "../components/Message.svelte";
    export let user = {};
    export let selectedRoomID = null;
    let messages = [];

    const getRoomMessages = () => {
        return new Promise((resolve, reject) => {
            console.log("Fetching room messages");
            $state.socket.emit("fetch_room_messages", selectedRoomID);

            $state.socket.on("fetch_room_messages_response", (data) => {
                // console.log("Got response from server", data);
                if (data?.successful) {
                    data.messages.map((m) => {
                        m.timestamp = new Date(m.timestamp);
                    });
                    resolve(data.messages);
                } else {
                    console.error(
                        "Error in fetching room messages:",
                        data?.description,
                    );
                    reject(data?.description);
                }
            });
        });
    };

    const fetchMessages = async () => {
        try {
            if (selectedRoomID === null) {
                console.log("Null user. Waiting for update");
                return;
            }
            messages = await getRoomMessages();
        } catch (error) {
            console.error("Error fetching user chats:", error);
        }
    };

    $: selectedRoomID, fetchMessages();
</script>

<h1>Chat Name</h1>
<div>
    {#each messages as message}
        <Message
            bind:current_user={user.username}
            bind:sender={message.sender}
            bind:content={message.content}
            bind:timestamp={message.timestamp}
        />
    {/each}
</div>
