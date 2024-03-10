<script>
    import { onMount } from "svelte";
    import { state } from "../stores/state_store.js";
    import ChatSelector from "../components/ChatSelector.svelte";
    import UserInfo from "../components/UserInfo.svelte";
    import Chat from "../components/Chat.svelte";
    import { navOptions } from "../components/Nav.svelte";

    let selected = navOptions[0]; // keep track of the selected 'page' object 
    import Nav from "./Nav.svelte";
    import ChatRoom from "./ChatRoom.svelte";
    let intSelected = 0; //selected page index

    let user = {};
    let selectedRoomID = null;

    function handleRoomSelection(roomID) {
        console.log("CHANGING TO ROOM", roomID);
        selectedRoomID = roomID;
    }
    
    // chcange the selected component (event.srcElement.id refers to the ID attribute of the HTL element that triggered the event)
    function changeComponent(event) {
        selected = navOptions[event.srcElement.id]
        intSelected = event.srcElement.id;
    }

</script>
<!-- Include Bootstrap CSS-->
<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'>
<div id="app">
    <div id="sidebar">
        <UserInfo bind:user />
        <ChatSelector {handleRoomSelection} />
    </div>
    <div id="page">
        <!--app navigation -->
        <ul class="nav nav-tabs">
            {#each navOptions as option, i}
            <li class="nav-item">
                <button class={intSelected == i ? "nav-link active p-2 ml-1" : "p-2 ml-1 nav-link"} on:click={changeComponent} id={i} role="tab">{option.page}</button>
            </li>
            {/each}
        </ul>
        <div id="page-content">
            <svelte:component this={selected.component} user={user} selectedRoomID={selectedRoomID} />
        </div>
    </div>
</div>

<style>
    #app {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        display: flex;
        height: 100vh;
        width: 100%;
    }

    #sidebar {
        width: 250px;
        background-color: #2c3e50; /* Dark background color */
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        color: white; /* Text color */
    }

    #page {
        display: flex;
        flex-direction: column;
        margin-bottom: 20px; /* Adjust as needed */
        width: 100%;
    }

    #page-content {
        margin-top: 10px;
    }
</style>
