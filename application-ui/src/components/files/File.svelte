<script>
    import FileUpload from "./FileUpload.svelte";

    export let user;
    export let selectedRoomID;
    let content = '';

</script>

<div id="file">
    {#if selectedRoomID !== null}
        {content}
    {/if}
    
    <FileUpload bind:content={content}/>
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
