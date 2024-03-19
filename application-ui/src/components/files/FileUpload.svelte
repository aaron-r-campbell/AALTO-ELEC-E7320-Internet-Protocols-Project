<script>
    import { onMount } from "svelte";
    import { state } from "../../stores/state_store.js";

    export let selectedRoomID;
    let hidden;

    onMount(() => {
        hidden = true;
        console.log(hidden);
    });

    async function handleFileChange(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = () => {
            const charlist = reader.result.split("");
            const crdtArray = charlist.map((char, index) => {
                return { value: char, position: index + 1.0 };
            });
            $state.socket.emit(
                "upload_document",
                selectedRoomID,
                crdtArray,
                file,
            );
            $state.socket.on("fetch_room_files_response", () => {
                if (payload.successful) {
                    console.log("Upload file successful");
                } else {
                    console.error("Upload file unsuccessful");
                }
            });
        };
        reader.onerror = () => {
            console.log(reader.error);
        };
    }
</script>

<div>
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
                    console.log("button clicked");
                }}>Submit</button
            >
        </div>
    </div>
</div>
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
