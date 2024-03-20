<script>
  import { state } from "/app/src/stores/state_store.js";

  let roomName = "";

  function handleSubmit(event) {
    event.preventDefault();

    // Add your logic here to create a room with the roomName
    console.log("Creating room with name:", roomName);

    // This returns "return_user_rooms" event with all rooms of the user which is handled in ChatSelector
    $state.socket.emit("create_room", roomName);

    roomName = "";
  }
</script>

<form on:submit={handleSubmit}>
  <label for="roomNameInput">Room name:</label>
  <input
    type="text"
    id="roomNameInput"
    placeholder="Enter room name"
    bind:value={roomName}
  />
  <button type="submit">Create Room</button>
</form>
