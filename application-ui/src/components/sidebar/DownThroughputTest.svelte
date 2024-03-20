<script>
  import axios from "axios";

  let throughputMbps = null;
  let sizeKB = 1024; // Default size: 1 MB
  let isDisabled = false;

  // Function to initiate the download request
  const downloadTest = async () => {
    try {
      let delay_milliseconds = 0;

      // Iteratively increase delay until test lasts longer than 10 seconds
      while (delay_milliseconds < 5000) {
        console.log("Previous delay:", delay_milliseconds);
        const url = `/api/throughput_download?size_kb=${sizeKB}`;

        const start = Date.now();

        await axios.get(url, {
          responseType: "blob",
          timeout: 30000,
        });

        const end = Date.now();

        delay_milliseconds = end - start;

        // Maybe looks nicer when the value updates during the test
        if (delay_milliseconds > 0) {
          throughputMbps = Math.trunc(
            (8 * sizeKB) / (delay_milliseconds / 1000) / 1024,
          );
        }

        sizeKB = sizeKB * 2;
      }

      // Reset the sizeKB for future tests
      sizeKB = 1024;

      // Save the response data into a variable
    } catch (error) {
      console.error("Error downloading file:", error);
      return null; // Return null in case of error
    }
  };

  const handleSubmit = async () => {
    isDisabled = true;
    await downloadTest();
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
    <p>Download throughput estimate: {throughputMbps} Mbps</p>
  {:else}
    <p>No download throughput estimate available</p>
  {/if}
</div>
