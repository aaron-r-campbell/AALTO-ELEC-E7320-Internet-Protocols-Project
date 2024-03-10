<script>
    import Chat from "../Chat.svelte";
    import axios from "axios";
    import FileUpload from "./FileUpload.svelte";

    export let user;
    export let selectedRoomID;
    let content = '';

    async function handleFileChange(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        render.onload = () => {
            content = reader.result;
            console.log(reader.result);
        }
        render.onerror = () => {
            console.log(reader.error);
        }
        reader.readAsText(file)
    }
</script>

<div id="files">
    {#if selectedRoomID !== null}
        {content}
    {/if}
    
    <FileUpload bind:content={content}/>
</div>

<style>
    #files {
        height: 100%;
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #ecf0f1; /* Light background color */
    }
</style>
