<script>
    import { state } from "/app/src/stores/state_store.js";

    import Message from "/app/src/components/chat/Message.svelte";

    export let user = {},
        selectedRoom = null;

    let messages = [];

    const getRoomMessages = () => {
        return new Promise((resolve, reject) => {
            console.log("Fetching room messages");
            $state.socket.emit("fetch_room_messages", selectedRoom.room_id);

            // Don't fetch messages for the other chats that might have been previously open
            $state.socket.off("fetch_room_messages_response");

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
            if (selectedRoom.room_id === null) {
                console.log("Null user. Waiting for update");
                return;
            }
            // Initially get all messages
            messages = await getRoomMessages();

            // Then start listening to the instant messages
            $state.socket.off("receive_msg");

            $state.socket.on("receive_msg", (data) => {
                console.log("Received message from room", data.room_id);
                if (data.room_id !== selectedRoom.room_id) {
                    reject("Not in currently selected room");
                }

                if (data?.successful) {
                    const new_message = data.data;

                    new_message.timestamp = new Date(data.data.timestamp);

                    console.log(
                        "Updating the messages array with",
                        new_message,
                    );

                    messages = [...messages, new_message];
                    console.log("Current messages:", messages);
                } else {
                    console.error(
                        "Error in fetching room messages:",
                        data?.description,
                    );
                    throw new Error(data?.description);
                }
            });
        } catch (error) {
            console.error("Error fetching user chats:", error);
        }
    };

    $: {
        if (selectedRoom && selectedRoom.room_id !== null) {
            fetchMessages();
        }
    }
</script>

<div
    style="flex: 1; display: flex; flex-direction: column-reverse; gap: 16px; overflow-y: scroll; padding: 16px"
>
    {#each messages.slice().reverse() as message}
        <Message
            bind:current_user={user.username}
            bind:sender={message.sender}
            bind:content={message.content}
            bind:timestamp={message.timestamp}
        />
    {/each}
</div>
