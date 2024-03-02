<script>
    let chats = [{ name: "Chat 1" }, { name: "Chat 2" }, { name: "Chat 3" }];
</script>

<ul id="chats-list">
    {#each chats as chat}
        <li>{chat.name}</li>
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
