<script>
    import { onMount } from "svelte";
    import { state } from "../../stores/state_store.js";
    import File from "./File.svelte";
    import FileUpload from "./FileUpload.svelte";

    export let user, selectedRoomID;
    let files = [],
        selectedFileId;

    onMount(() => {
        $state.socket.emit("fetch_room_files");
        $state.socket.on("fetch_room_files_response", (payload) => {
            if (payload.successful) {
                console.log("GOT ROOM FILES:", payload.files);
                files = payload.files;
            } else {
                console.error(
                    "Did not get room files:",
                    payload.description,
                );
            }
        });
    });
</script>

<div id="file">
    {#if selectedRoomID !== null}
        <ul>
            {#each files as file}
                <button on:click={() => selectedFileId = file.id}>file.name</button>
            {/each}
        </ul>
        {#if selectedFileId}
            <File bind:selectedFileId />
        {/if}
        <FileUpload bind:selectedRoomID />
    {/if}
</div>

<style>
    #file {
        height: 100%;
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #ecf0f1; /* Light background color */
    }
</style>
