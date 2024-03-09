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

    // {
    //     sender: "Alice",
    //     content: "Hey, how are you?",
    //     timestamp: new Date("2024-02-24T10:15:00"),
    // },
    // {
    //     sender: "Bob",
    //     content: "I'm good, thanks! How about you?",
    //     timestamp: new Date("2024-02-24T10:16:30"),
    // },
    // {
    //     sender: "Alice",
    //     content: "I'm doing well too, just had a busy day at work.",
    //     timestamp: new Date("2024-02-24T10:17:45"),
    // },
    // {
    //     sender: "user1",
    //     content: "Hello everyone! What's up?",
    //     timestamp: new Date("2024-02-24T10:18:30"),
    // },
    // {
    //     sender: "Bob",
    //     content: "Hey user1! We're just chatting about our day.",
    //     timestamp: new Date("2024-02-24T10:19:15"),
    // },
    // {
    //     sender: "David",
    //     content: "Hi folks! Anything interesting going on?",
    //     timestamp: new Date("2024-02-24T10:20:00"),
    // },
    // {
    //     sender: "Alice",
    //     content: "Not much, just planning a relaxing weekend. You?",
    //     timestamp: new Date("2024-02-24T10:21:30"),
    // },
    // {
    //     sender: "Eva",
    //     content: "Hey everyone! Mind if I join the chat?",
    //     timestamp: new Date("2024-02-24T10:22:45"),
    // },
    // {
    //     sender: "user1",
    //     content: "Of course, Eva! The more, the merrier!",
    //     timestamp: new Date("2024-02-24T10:23:15"),
    // },
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
