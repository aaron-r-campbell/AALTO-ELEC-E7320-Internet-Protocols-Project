<script>
  import { onMount, onDestroy } from "svelte";
  import { state } from "../stores/state_store.js";

  export let selectedRoomID;

  let users_not_in_room = [];

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
    $state.socket.emit("get_users_not_in_room", selectedRoomID);
  };

  // Runs every time selectedRoomID changes AFAIK
  $: {
    selectedRoomID, getUsersNotInRoom();
  }

  let selectedUser = "";

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Inviting user", selectedUser, "to chatroom");
    $state.socket.emit("add_to_room", selectedRoomID, selectedUser);

    $state.socket.once("add_to_room_response", (payload) => {
      if (payload.successful) {
        console.log("User added to room successfully");
        // Refetch the list
        $state.socket.emit("get_users_not_in_room", selectedRoomID);
      } else {
        console.error("Got error:", payload.description);
      }
    });
  }
</script>

<form on:submit={handleSubmit}>
  <label for="userSelect">Invite a user:</label>
  <select id="userSelect" bind:value={selectedUser}>
    {#each users_not_in_room as user}
      <option value={user}>{user}</option>
    {/each}
  </select>
  <button type="submit">Submit</button>
</form>
