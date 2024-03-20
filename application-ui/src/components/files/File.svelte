<script>
    import FileUpload from "../../components/files/FileUpload.svelte";
    import { onMount } from "svelte";
    import { state } from "../../stores/state_store.js";

    export let selectedFileId;
    let textarea,
        content,
        crdtArray = [];

    function handleEdit(event) {
        const cursorPosition = event.target.selectionStart;

        const changeType = event.inputType;
        let insertedChar = event.data; // Inserted character

        // console.log(content);
        console.log(crdtArray);
        console.log("Change:", event);

        console.log("cursorPosition", cursorPosition);
        console.log("changeType", changeType);
        console.log("insertedChar", insertedChar);
        console.log("lenght", crdtArray.length);

        if (changeType == "insertLineBreak") {
            insertedChar = "\n";
        }

        // const token_at_cursorposition = crdtArray[cursorPosition];

        // console.log("token_at_cursorposition", token_at_cursorposition);

        // Determine the index of the CRDT array corresponding to the cursor position

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
            const cursor_start_index = cursorPosition - 1;
            // const crdtIndex =
            //     crdtArray.findIndex(
            //         (char) => char.position >= token_at_cursorposition.position,
            //     ) || crdtArray.length;
            // Insertion logic
            console.log("HELO");
            let newPosition;
            if (crdtArray.length === 0) {
                console.log("Insertion to empty");
                // If the CRDT array is empty, the new character should start with position 1
                newPosition = 1;
            } else if (cursor_start_index === 0) {
                // Insertion at the beginning of the text
                console.log("Inserting to beginning");
                newPosition = crdtArray[0].position / 2;
            } else if (cursor_start_index === crdtArray.length) {
                // Insertion at the end of the text
                console.log("Inserting to end");
                console.log(crdtArray[crdtArray.length - 1]);
                newPosition = crdtArray[cursor_start_index - 1].position + 1;
            } else {
                console.log("Insertion between");
                // Insertion between characters
                const prevPosition = crdtArray[cursor_start_index - 1].position;
                const nextPosition = crdtArray[cursor_start_index].position;
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
    }

    const getFileContents = async () => {
        console.log("Getting file contents");
        return new Promise((resolve, reject) => {
            console.log("Emitting join_file_edit");
            $state.socket.emit("join_file_edit", selectedFileId);

            // Stop getting updates from other files
            $state.socket.off("join_file_edit_response");

            $state.socket.on("join_file_edit_response", (data) => {
                console.log("GOT join_file_edit_response", data);
                if (data?.successful) {
                    // console.log("Here is the data:", data);
                    console.log(
                        `User has joined to edit the file: ${selectedFileId}`,
                    );
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
        console.log("Fetching file contents");
        try {
            if (selectedFileId === null) {
                console.log("Null user. Waiting for update");
                return;
            }
            // Initially get all messages
            crdtArray = await getFileContents();
            console.log("THIS IS THE CRDT ARRAY:", crdtArray);
            content = crdtArray
                .sort((a, b) => a.position - b.position)
                .map((obj) => obj.char)
                .join("");

            console.log("content", content);

            // Then start listening to the instant messages
            $state.socket.off("update_file_response");

            $state.socket.on("update_file_response", (response) => {
                console.log(
                    `update_file_response, char: {response.data.char} position: {response.data.position}`,
                );
                if (response.data.file_id !== selectedFileId) {
                    console.log("Here1");
                    console.log("Not in currently selected file");
                    console.log(`data.file_id = ${response.data.file_id}`);
                    console.log(`selelcted file id = ${selectedFileId}`);
                }
                if (response?.successful) {
                    console.log("Here2");
                    crdtArray = [
                        ...crdtArray,
                        {
                            char: response.data.char,
                            position: response.data.position,
                        },
                    ];
                    console.log("Setting content");
                    content = crdtArray
                        .sort((a, b) => a.position - b.position)
                        .map((obj) => obj.char)
                        .join("");
                    console.log("content:", content);
                    console.log("crdtArray:", crdtArray);
                } else {
                    console.error(
                        "Error in fetching file update:",
                        response?.description,
                    );
                    throw new Error(response?.description);
                }
            });
        } catch (error) {
            console.error("Error fetching file data:", error);
        }
    };

    onMount(() => {});

    $: selectedFileId, fetchFileContents();
</script>

<textarea
    style="height: 90%; width: 100%;"
    bind:this={textarea}
    on:input={handleEdit}
    bind:value={content}
></textarea>
