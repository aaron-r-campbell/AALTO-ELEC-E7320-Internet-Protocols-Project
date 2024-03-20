<script>
  import { onMount, onDestroy } from "svelte";
  import { state } from "/app/src/stores/state_store.js";

  export let selectedRoom;

  let users_not_in_room = [],
    modalVisible = false,
    selectedUser = "";

  // For fetching the list of users who can be invited to a room
  onMount(async () => {
    try {
      $state.socket.on("get_users_not_in_room_response", (payload) => {
        console.log("THIS IS THE PAYLOAD FOR USERS NOT IN ROOM:", payload);
        if (payload.successful) {
          users_not_in_room = payload.data.map((x) => x.username);
        } else {
          throw new Error(payload.description);
        }
      });
    } catch (error) {
      console.error("Error fetching user chats:", error);
    }
  });

  onDestroy(() => {
    $state.socket.off("get_users_not_in_room_response");
  });

  const getUsersNotInRoom = async () => {
    $state.socket.emit("get_users_not_in_room", selectedRoom.room_id);
  };

  // Runs every time selectedRoom.room_id changes AFAIK
  $: {
    selectedRoom.room_id, getUsersNotInRoom();
  }

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Inviting user", selectedUser, "to chatroom");
    $state.socket.emit("add_to_room", selectedRoom.room_id, selectedUser);

    $state.socket.once("add_to_room_response", (payload) => {
      if (payload.successful) {
        console.log("User added to room successfully");
        // Refetch the list
        $state.socket.emit("get_users_not_in_room", selectedRoom.room_id);
      } else {
        console.error("Got error:", payload.description);
      }
    });
  }

  function setModal(visible) {
    modalVisible = visible;
  }
</script>

<button type="button" on:click={() => setModal(true)}
  >Invite User</button
>

{#if modalVisible}
  <div class="centerModal card" style={modalVisible ? "block" : "none"}>
    <h2>Create Chatroom</h2>
    <form on:submit={handleSubmit}>
      <label for="userSelect">User to add:</label>
      <select id="userSelect" class="fw" bind:value={selectedUser}>
        <option value="" disabled selected hidden>Select a user</option>
        {#each users_not_in_room as user}
          <option value={user}>{user}</option>
        {/each}
      </select>
      <div style="display:flex; justify-content: flex-end; gap: 16px;">
        <button type="button" class="red-bg" on:click={() => setModal(false)}
          >Cancel</button
        >
        <button type="submit">Add User</button>
      </div>
    </form>
  </div>
{/if}
