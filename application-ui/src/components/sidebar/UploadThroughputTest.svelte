<script>
  import axios from "axios";

  let modalContent = [];
  let testRunning = false;
  let modalVisible = false;

  const uploadTest = async () => {
    let sizeMB = 1,
      totalSizeMB = 0,
      totalDurationsMilliseconds = 0;

    setModal(true);
    testRunning = true;

    while (testRunning && sizeMB <= 1024) {
      const start = Date.now();

      try {
        const payload = new Uint8Array(sizeMB * 1024 * 1024);
        crypto.getRandomValues(payload);
        await axios.post("/api/throughput_upload", payload.buffer, {
          headers: {
            "Content-Type": "application/octet-stream",
          },
          responseType: "json",
        });
      } catch (error) {
        console.error("Error uploading file:", error);
        modalContent = [
          ...modalContent,
          "Error uploading file. Please try again.",
        ];
        break;
      }

      const end = Date.now();
      const durationMilliseconds = end - start;

      modalContent = [
        ...modalContent,
        `Uploaded ${sizeMB} MB file in ${durationMilliseconds} ms`,
      ];

      if (durationMilliseconds > 0) {
        totalSizeMB += sizeMB;
        totalDurationsMilliseconds += durationMilliseconds;
      }

      if (durationMilliseconds >= 5000) break;

      sizeMB *= 2;
    }

    modalContent = [
      ...modalContent,
      `Upload throughput estimate: ${Math.trunc(8000 * (totalSizeMB / totalDurationsMilliseconds))} Mbps`,
    ];

    testRunning = false;
  };

  function setModal(visible) {
    modalVisible = visible;
  }
</script>

<div>
  <button
    on:click={uploadTest}
    disabled={testRunning}
    class="fw"
    style={testRunning ? "background-color: grey; cursor: not-allowed; width: 50%;" : "width: 50%;"}
  >
    Upload Test
  </button>
  {#if modalVisible}
    <div class="centerModal card" style="color: var(--text-color);">
      <h2>Upload Test</h2>
      {#each modalContent as element}
        <p>{element}</p>
      {/each}
      <div style="display:flex; justify-content: flex-end; gap: 16px;">
        <button
          type="button"
          class={testRunning ? "red-bg" : ""}
          on:click={() => {
            testRunning = false;
            modalContent = [];
            setModal(false);
          }}>{testRunning ? "Cancel" : "Ok"}</button
        >
      </div>
    </div>
  {/if}
</div>
