<script>
    import FileUpload from "/app/src/components/files/FileUpload.svelte";
    import { onMount } from "svelte";
    import { state } from "../../stores/state_store.js";

    export let selectedFileId;
    let textarea, content,
        crdtArray = [];

    function handleEdit(event) {
        console.log("Change:", event);

        const cursorPosition = event.target.selectionStart;
        const changeType = event.inputType;
        const insertedChar = event.data; // Inserted character

        // Determine the index of the CRDT array corresponding to the cursor position
        const crdtIndex =
            crdtArray.findIndex((char) => char.position >= cursorPosition) ||
            crdtArray.length;

        if (changeType === "deleteContentBackward") {
            // Deletion logic
            const deletedCharPosition = cursorPosition;
            const charToDeleteIndex = crdtArray.findIndex(
                (char) => char.position === deletedCharPosition,
            );
            if (charToDeleteIndex !== -1) {
                crdtArray.splice(charToDeleteIndex, 1);
                // Update positions of subsequent characters in the CRDT array
                for (let i = charToDeleteIndex; i < crdtArray.length; i++) {
                    crdtArray[i].position--;
                }
            }
        } else {
            // Insertion logic
            let newPosition;
            if (crdtArray.length === 0) {
                // If the CRDT array is empty, the new character should start with position 1
                newPosition = 1;
            } else if (crdtIndex === 0) {
                // Insertion at the beginning of the text
                newPosition = crdtArray[0].position / 2;
            } else if (crdtIndex === crdtArray.length) {
                // Insertion at the end of the text
                newPosition = crdtArray[crdtArray.length - 1].position + 1;
            } else {
                // Insertion between characters
                const prevPosition = crdtArray[crdtIndex - 1].position;
                const nextPosition = crdtArray[crdtIndex].position;
                newPosition = (prevPosition + nextPosition) / 2;
            }

            $state.socket.emit(
                "update_file",
                selectedFileId,
                changeType,
                insertedChar,
                newPosition,
            );
        }

        console.log("Updated CRDT array:", crdtArray);
    }

    const getFileContents = () => {
        return new Promise((resolve, reject) => {
            $state.socket.emit("join_file_edit", selectedFileId);

            // Stop getting updates from other files
            $state.socket.off("join_file_edit_response");

            $state.socket.on("join_file_edit_response", (data) => {
                if (data?.successful) {
                    resolve(data.data);
                } else {
                    console.error(
                        "Error in fetching room messages:",
                        data?.description,
                    );
                    reject(data?.description);
                }
            });
        });
    };
    const fetchFileContents = async () => {
        try {
            if (selectedFileId === null) {
                console.log("Null user. Waiting for update");
                return;
            }
            // Initially get all messages
            messages = await getFileContents();

            // Then start listening to the instant messages
            $state.socket.off("update_file");

            $state.socket.on("update_file", (data) => {
                if (data.file_id !== selectedFileId) {
                    reject("Not in currently selected file");
                }

                if (data?.successful) {
                    crdtArray = [
                        ...crdtArray,
                        { char: data.char, position: data.position },
                    ];
                    content = crdtArray
                        .sort((a, b) => a.position - b.position)
                        .map(obj => obj.char)
                        .join('');
                } else {
                    console.error(
                        "Error in fetching file update:",
                        data?.description,
                    );
                    throw new Error(data?.description);
                }
            });
        } catch (error) {
            console.error("Error fetching file data:", error);
        }
    };

    $: selectedFileId, fetchFileContents();
</script>

<textarea
    style="height: 90%; width: 100%;"
    bind:this={textarea}
    on:input={handleEdit}
    bind:value={content}
></textarea>
