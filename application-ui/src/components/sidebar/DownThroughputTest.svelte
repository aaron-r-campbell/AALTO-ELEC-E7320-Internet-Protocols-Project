<script>
  import axios from "axios";

  let modalContent = [],
    testRunning = false,
    modalVisible = false;

  const downloadTest = async () => {
    let sizeMB = 1,
      totalSizeMB = 0,
      totalDurationMilliseconds = 0;

    setModal(true);
    testRunning = true;

    while (testRunning && sizeMB <= 1024) {
      const start = Date.now();

      try {
        await axios.get(`/api/throughput_download?size_kb=${sizeMB * 1024}`, {
          responseType: "blob",
          timeout: 30000,
        });
      } catch (error) {
        console.error("Error downloading file:", error);
        modalContent = [
          ...modalContent,
          "Error downloading file. Please try again.",
        ];
        break;
      }

      const end = Date.now();
      const durationMilliseconds = end - start;

      modalContent = [
        ...modalContent,
        `Downloaded ${sizeMB} MB file in ${durationMilliseconds} ms`,
      ];

      if (durationMilliseconds > 0) {
        totalSizeMB += sizeMB;
        totalDurationMilliseconds += durationMilliseconds;
      }

      if (durationMilliseconds >= 5000) break;

      sizeMB *= 2;
    }

    modalContent = [
      ...modalContent,
      `Download throughput estimate: ${Math.trunc(8000 * (totalSizeMB / totalDurationMilliseconds))} Mbps`,
    ];

    testRunning = false;
  };

  function setModal(visible) {
    modalVisible = visible;
  }
</script>

<div>
  <button
    on:click={downloadTest}
    disabled={testRunning}
    class="fw"
    style={testRunning ? "background-color: grey; cursor: not-allowed; width: 50%;" : "width: 50%;"}
  >
    Download Test
  </button>
  {#if modalVisible}
    <div class="centerModal card" style="color: var(--text-color);">
      <h2>Download Test</h2>
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
