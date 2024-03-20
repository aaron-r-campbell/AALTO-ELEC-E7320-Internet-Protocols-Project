<script>
  import { state } from "/app/src/stores/state_store.js";

  export let user = null;
  export let selectedRoom = null;

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
    console.log("roomid:", selectedRoom.room_id);

    $state.socket.emit("send_msg", message, selectedRoom.room_id);

    message = "";
  }
</script>

<div id="input-container">
  <input
    type="text"
    placeholder="Type your message..."
    style="width: calc(100% - 32px); margin: 16px;"
    bind:value={message}
    on:keydown={handleKeyPress}
  />
</div>
