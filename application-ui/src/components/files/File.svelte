<script>
    import FileUpload from "/app/src/components/files/FileUpload.svelte";

    export let selectedRoom;
    let editableDiv;

    let objects = [];

    // Function to update the objects array when the div content is edited
    function handleEdit(event) {
        const content = event.target.textContent;

        // Update objects array based on the edited content
        const newObjects = content.split("").map((char, index) => {
            const position = index + 0.5; // Assume halfway between characters
            const obj = { value: char, position: position };
            return obj;
        });

        logChanges(objects, newObjects);
        objects = newObjects;

        updateEditableDiv();
    }

    // Function to update the editable div content based on the objects array
    function updateEditableDiv() {
        objects.sort((a, b) => a.position - b.position);
        editableDiv.innerHTML = objects.map((obj) => obj.value).join("");
    }

    // Function to log changes in objects
    function logChanges(oldObjects, newObjects) {
        oldObjects.forEach((oldObj) => {
            const newObj = newObjects.find((obj) => obj.value === oldObj.value);
            if (!newObj) {
                console.log(
                    `Removed '${oldObj.value}' from position ${oldObj.position}`,
                );
            }
        });

        newObjects.forEach((newObj) => {
            const oldObj = oldObjects.find((obj) => obj.value === newObj.value);
            if (!oldObj) {
                console.log(
                    `Added '${newObj.value}' in position ${newObj.position}`,
                );
            }
        });
    }

    let callback = () => {
        updateEditableDiv();
    };
</script>

<div id="file">
    {#if selectedRoom.room_id !== null}
        <div
            bind:this={editableDiv}
            contenteditable="true"
            on:input={handleEdit}
        ></div>
    {/if}

    <FileUpload bind:objects bind:callback />
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
