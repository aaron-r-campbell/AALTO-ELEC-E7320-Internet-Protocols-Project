<script>
  import { state } from "../stores/state_store.js";

  export let user = null;
  export let selectedRoomID = null;

  let message = "";

  function handleKeyPress(event) {
    if (event.key === "Enter") {
      sendMessage();
      event.preventDefault();
    }
  }

  function sendMessage() {
    console.log("Message sent:", message);
    console.log("user:", user);
    console.log("roomid:", selectedRoomID);

    $state.socket.emit("send_msg", message, selectedRoomID);

    message = "";
  }
</script>

<div id="input-container">
  <input
    type="text"
    placeholder="Type your message..."
    bind:value={message}
    on:keydown={handleKeyPress}
  />
</div>

<style>
  #input-container {
    padding: 20px;
  }
</style>
