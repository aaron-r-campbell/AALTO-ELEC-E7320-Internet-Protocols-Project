<script>
  import { state } from "/app/src/stores/state_store.js";

  let roomName = "";

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Creating room with name:", roomName);

    // This returns "return_user_rooms" event with all rooms of the user which is handled in ChatSelector
    $state.socket.emit("create_room", roomName);

    roomName = "";
    closeCreateRoomModal();
  }

  function openCreateRoomModal() {
    document.getElementById("createRoomModal").style.display = "block";
  }

  function closeCreateRoomModal() {
    document.getElementById("createRoomModal").style.display = "none";
  }
</script>

<button
  type="button"
  style="height: 100%;"
  on:click={openCreateRoomModal}>Create Room</button
>

<div id="createRoomModal" class="card">
  <h2>Create Chatroom</h2>
  <form on:submit={handleSubmit}>
    <label for="roomNameInput">Room name:</label>
    <input
      type="text"
      id="roomNameInput"
      bind:value={roomName}
      placeholder="Enter room name"
    />
    <div style="display:flex; justify-content: flex-end; gap: 16px;">
      <button type="button" class="red-button" on:click={closeCreateRoomModal}
        >Cancel</button
      >
      <button type="submit">Create</button>
    </div>
  </form>
</div>

<style>
  #createRoomModal {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: var(--text-color);
  }

  .red-button {
    background-color: var(--primary-red);
  }
  .red-button:hover {
    background-color: var(--primary-hover-red);
  }
</style>
