<script>
    import Message from "../components/Message.svelte";

    export let current_user = "user1";

    let messages = [
        {
            sender: "Alice",
            content: "Hey, how are you?",
            timestamp: new Date("2024-02-24T10:15:00"),
        },
        {
            sender: "Bob",
            content: "I'm good, thanks! How about you?",
            timestamp: new Date("2024-02-24T10:16:30"),
        },
        {
            sender: "Alice",
            content: "I'm doing well too, just had a busy day at work.",
            timestamp: new Date("2024-02-24T10:17:45"),
        },
        {
            sender: "user1",
            content: "Hello everyone! What's up?",
            timestamp: new Date("2024-02-24T10:18:30"),
        },
        {
            sender: "Bob",
            content: "Hey user1! We're just chatting about our day.",
            timestamp: new Date("2024-02-24T10:19:15"),
        },
        {
            sender: "David",
            content: "Hi folks! Anything interesting going on?",
            timestamp: new Date("2024-02-24T10:20:00"),
        },
        {
            sender: "Alice",
            content: "Not much, just planning a relaxing weekend. You?",
            timestamp: new Date("2024-02-24T10:21:30"),
        },
        {
            sender: "Eva",
            content: "Hey everyone! Mind if I join the chat?",
            timestamp: new Date("2024-02-24T10:22:45"),
        },
        {
            sender: "user1",
            content: "Of course, Eva! The more, the merrier!",
            timestamp: new Date("2024-02-24T10:23:15"),
        },
    ];
</script>

<h1>Chat Name</h1>
<div>
    {#each messages as message}
        <Message
            bind:current_user
            bind:sender={message.sender}
            bind:content={message.content}
            bind:timestamp={message.timestamp}
        />
    {/each}
</div>
