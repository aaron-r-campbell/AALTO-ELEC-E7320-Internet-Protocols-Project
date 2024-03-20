<script>
  import { state } from "/app/src/stores/state_store.js";

  export let selectedRoom;

  function removeRoom(event) {
    event.preventDefault();

    $state.socket.emit("remove_room", selectedRoom.room_id);
    // The response logic is handled in ChatSelector.svelte on "remove_room_response"
  }
</script>

<button on:click={removeRoom}>Remove room</button>
