<script>
  import { state } from "/app/src/stores/state_store.js";

  let roomName = "",
    modalVisible = false;

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Creating room with name:", roomName);

    // This returns "return_user_rooms" event with all rooms of the user which is handled in ChatSelector
    $state.socket.emit("create_room", roomName);

    roomName = "";
    closeCreateRoomModal();
  }

  function setModal(visible) {
    modalVisible = visible;
  }
</script>

<button type="button" style="height: 100%;" on:click={() => setModal(true)}
  >Create Room</button
>

{#if modalVisible}
  <div class="centerModal card" style="color: var(--text-color);">
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
        <button type="button" class="red-bg" on:click={() => setModal(false)}
          >Cancel</button
        >
        <button type="submit">Create</button>
      </div>
    </form>
  </div>
{/if}
