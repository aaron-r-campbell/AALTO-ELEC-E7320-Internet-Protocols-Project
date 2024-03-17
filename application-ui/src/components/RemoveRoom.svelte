<script>
  import { state } from "../stores/state_store.js";

  export let selectedRoomID;

  function removeRoom(event) {
    event.preventDefault();

    $state.socket.emit("remove_room", selectedRoomID);
    // The response logic is handled in ChatSelector.svelte on "remove_room_response"
  }
</script>

<button on:click={removeRoom}>Remove room</button>
