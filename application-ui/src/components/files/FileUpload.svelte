<script>
    import { onMount } from "svelte";
    import { state } from "../../stores/state_store.js";

    export let selectedRoom;
    let hidden = true;

    // onMount(() => {
    //     hidden = true;
    //     console.log(hidden);
    // });

    let selectedFile = null;
    let fileContents = null;
    let emptyFileName = "";

    async function handleFileChange(event) {
        console.log("In handleFileChange");
        const file = event.target.files[0];
        console.log("FILE:", file);
        if (!file) return;
        selectedFile = file;

        const reader = new FileReader();

        reader.onload = () => {
            fileContents = reader.result;
            console.log("In onload", fileContents);
        };
        reader.onerror = () => {
            console.log(reader.error);
        };

        reader.readAsText(selectedFile);
    }

    async function handleFileUpload() {
        hidden = true;
        console.log("Inside handleButton");
        console.log("selectedFile:", selectedFile);
        if (!selectedFile) return;

        const charlist = fileContents.split("");
        console.log("Getting charlist:", charlist);

        const crdtArray = charlist.map((char, index) => {
            return { char: char, position: index + 1.0 };
        });
        console.log("This is the charlist", charlist);
        console.log("This is the crdtArray", crdtArray);
        $state.socket.emit(
            "upload_document",
            selectedRoom.room_id,
            crdtArray,
            selectedFile.name,
        );
        $state.socket.on("fetch_room_files_response", () => {
            if (payload.successful) {
                console.log("Upload file successful");
            } else {
                console.error("Upload file unsuccessful");
            }
        });
    }

    async function handleEmptyFile() {
        hidden = true;
        console.log("Inside handleEmptyFile");

        if (!emptyFileName) return;

        if (!emptyFileName.endsWith(".txt")) emptyFileName += ".txt";

        $state.socket.emit(
            "upload_document",
            selectedRoom.room_id,
            [],
            emptyFileName,
        );

        $state.socket.on("fetch_room_files_response", () => {
            if (payload.successful) {
                console.log("Upload file successful");
            } else {
                console.error("Upload file unsuccessful");
            }
        });
        emptyFileName = "";
    }
</script>

{#if !hidden}
    <div class="centerModal card" style={hidden ? "none" : "block"}>
        <div style="display: flex; gap: 16px; margin-bottom: 16px;">
            <div style="width: 50%;">
                <h3>Add Empty File</h3>
                <form on:submit={handleEmptyFile}>
                    <label for="emptyFileName">File Name:</label>
                    <input
                        style="width: 100%;"
                        type="text"
                        id="emptyFileName"
                        name="emptyFileName"
                        bind:value={emptyFileName}
                        required
                    />
                    <button type="submit">Create Empty File</button>
                </form>
            </div>
            <div style="width: 50%;">
                <h3>Upload File</h3>
                <form on:submit={handleFileUpload}>
                    <label for="fileToUpload">Choose File:</label>
                    <input
                        style="margin-bottom: 16px; padding: 10px;"
                        type="file"
                        id="fileToUpload"
                        name="fileToUpload"
                        required
                        accept=".txt"
                        on:change={handleFileChange}
                    />
                    <button type="submit">Upload File</button>
                </form>
            </div>
        </div>
        <button
            style="align-self: flex-end;"
            class="red-bg"
            on:click={() => (hidden = true)}>Close</button
        >
    </div>
{/if}

<button class="bottom-right-button" on:click={() => (hidden = false)}
    >New File</button
>

<style>
    .bottom-right-button {
        position: fixed;
        bottom: 20px; /* Adjust as needed */
        right: 20px; /* Adjust as needed */
    }
</style>
