<script>
    import ChatSelector from "../components/ChatSelector.svelte";
    import UserInfo from "../components/UserInfo.svelte";
    import Chat from "../components/Chat.svelte";

    let user;
</script>

<div id="app">
    <div id="sidebar">
        <UserInfo bind:user />
        <ChatSelector />
    </div>
    <div id="chats"><Chat bind:user /></div>
</div>

<!-- 
<h1>Welcome {username}!</h1>
<div style="display:flex;">
    <div style="width: 20vw; background-color: lightgray;">
        <h1>Chats:</h1>
        {#each chats as chat}
            <p>{chat.name}</p>
        {/each}
    </div>
    <div style="width: 80vw;"></div>
</div> -->

<style>
    #app {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        display: flex;
        height: 100vh;
    }
    #chats {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #ecf0f1; /* Light background color */
    }

    #sidebar {
        width: 250px;
        background-color: #2c3e50; /* Dark background color */
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        color: white; /* Text color */
    }
</style>
