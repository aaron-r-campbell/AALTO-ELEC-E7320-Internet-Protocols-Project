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

    async function handleButton() {
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
</script>

{#if !hidden}
    <div class="model" class:hidden>
        <div class="content">
            <button
                class="close-button"
                on:click={() => {
                    hidden = true;
                    console.log("button clicked");
                    console.log(hidden);
                }}>&times;</button
            >
            <div class="group">
                <label for="file">Upload your file</label>
                <input
                    type="file"
                    name="fileToUpload"
                    required
                    accept=".txt"
                    on:change={handleFileChange}
                />
            </div>
            <button
                type="submit"
                on:click={() => {
                    hidden = true;
                    console.log("Submit pressed");
                    handleButton();
                }}>Submit</button
            >
        </div>
    </div>
{/if}
<button class="bottom-right-button" on:click={() => (hidden = false)}
    >Upload</button
>

<style>
    .bottom-right-button {
        position: fixed;
        bottom: 20px; /* Adjust as needed */
        right: 20px; /* Adjust as needed */
    }
    .model {
        position: fixed;
        z-index: 9999;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgb(0, 0, 0);
        background-color: rgba(0, 0, 0, 0.4);
    }
    .content {
        position: relative;
        background-color: #fefefe;
        margin: 15% auto;
        padding: 20px;
        border: 1px solid #888;
        width: 80%;
    }
    .close-button {
        position: absolute;
        top: 0;
        right: 0.5rem;
        color: #aaa;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }
    .close-button:hover,
    .close-button:focus {
        color: black;
        text-decoration: none;
        cursor: pointer;
    }

    .hidden {
        display: none;
    }
</style>
