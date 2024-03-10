<script>
  import axios from "axios";

  let throughputMbps = null;
  let sizeKB = 1024; // Default size: 1 MB
  let isDisabled = false;

  // Function to initiate the download request
  const throughputTest = async (sizeKB) => {
    try {
      let delay_milliseconds = 0;

      // Iteratively increase delay until test lasts longer than 10 seconds
      while (delay_milliseconds < 10000) {
        console.log("Previous delay:", delay_milliseconds);
        const url = `http://localhost:7800/api/throughput_download?size_kb=${sizeKB}`;

        const start = Date.now();

        const response = await axios.get(url, {
          responseType: "blob",
          timeout: 30000,
        });

        const end = Date.now();

        delay_milliseconds = end - start;

        sizeKB = sizeKB * 2;
      }

      const result = Math.trunc(
        (8 * sizeKB) / (delay_milliseconds / 1000) / 1024,
      );

      sizeKB = 1024;

      // Save the response data into a variable
      return result;
    } catch (error) {
      console.error("Error downloading file:", error);
      return null; // Return null in case of error
    }
  };

  const handleSubmit = async () => {
    isDisabled = true;
    throughputMbps = await throughputTest(sizeKB);
    isDisabled = false;
  };
</script>

<div>
  <button
    on:click={handleSubmit}
    disabled={isDisabled}
    style={isDisabled ? "background-color: grey; cursor: not-allowed;" : ""}
  >
    Download test
  </button>
  {#if throughputMbps !== null}
    <p>Download throughput estimate: {throughputMbps} Kbps</p>
  {:else}
    <p>No throughput estimate available</p>
  {/if}
</div>
