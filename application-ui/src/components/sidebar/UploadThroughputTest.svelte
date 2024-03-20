<script>
  import axios from "axios";

  let throughputMbps = null;
  let sizeKB = 1024; // Default size: 1 MB
  let isDisabled = false;

  // Function to initiate the download request
  const uploadTest = async () => {
    try {
      let delay_milliseconds = 0;

      while (delay_milliseconds < 5000) {
        const payload = new Uint8Array(sizeKB * 1024).fill("A".charCodeAt(0));

        const start = Date.now();

        const response = await axios.post(
          "/api/throughput_upload",
          payload.buffer,
          {
            headers: {
              "Content-Type": "application/octet-stream",
            },
            responseType: "json",
          },
        );

        const end = Date.now();

        delay_milliseconds = end - start;

        console.log("Response:", response.data);
        console.log("Delay milliseconds:", delay_milliseconds);

        if (delay_milliseconds > 0) {
          throughputMbps = Math.trunc(
            (8 * sizeKB) / (delay_milliseconds / 1000) / 1024,
          );
        }

        sizeKB = sizeKB * 2;
      }
    } catch (error) {
      console.error("Error:", error.response.data);
    }
  };

  const handleSubmit = async () => {
    isDisabled = true;
    await uploadTest();
    isDisabled = false;
  };
</script>

<div>
  <button
    on:click={handleSubmit}
    disabled={isDisabled}
    style={isDisabled ? "background-color: grey; cursor: not-allowed;" : ""}
  >
    Upload test
  </button>
  {#if throughputMbps !== null}
    <p>Upload throughput estimate: {throughputMbps} Mbps</p>
  {:else}
    <p>No upload throughput estimate available</p>
  {/if}
</div>
