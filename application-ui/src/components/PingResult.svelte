<script>
  import { onMount } from "svelte";
  import { state } from "../stores/state_store.js";

  let value = null;

  onMount(() => {
    console.log("Starting to listen to pings");
    // Listen for events from the socket
    $state.socket.on("ping", (timestamp) => {
      // console.log("Received ping with timestamp:", timestamp);

      $state.socket.emit("ping_ack", timestamp);
    });

    $state.socket.on("ping_result", (RTT) => {
      // console.log("Received ping_result with value:", RTT);

      value = RTT;
    });
  });
</script>

<div>
  <p>
    Your current round-trip time to the server is {value} ms
  </p>
</div>
