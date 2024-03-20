<script>
  import { state } from "../../stores/state_store.js";

  export let file;

  const downloadTextFile = async () => {
    try {
      let fileContents = ""; // Initialize an empty string to accumulate file contents

      await new Promise((resolve, reject) => {
        $state.socket.emit("join_file_edit", file.id);

        $state.socket.on("join_file_edit_response", (data) => {
          if (!data?.successful) reject(new Error("Couldn't get file data."));
          console.log("data", data.data);

          // Accumulate file contents
          fileContents += data.data.map((obj) => obj.char).join("");

          resolve(); // Resolve the promise once all data is received
        });
      });

      console.log("fileContents", fileContents);
      const blob = new Blob([fileContents], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };
</script>

<button type="submit" on:click={downloadTextFile}>Download</button>
