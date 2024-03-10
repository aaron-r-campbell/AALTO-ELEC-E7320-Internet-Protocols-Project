<script>
  import { onMount } from "svelte";
  import { state } from "../stores/state_store.js";
  let users = [];

  onMount(() => {
    console.log("Starting to listen for user list");

    $state.socket.on("user_activities", (new_user_activities) => {
      console.log("Received new user list:", new_user_activities);

      users = new_user_activities;
    });

    $state.socket.on("user_activities_update", (new_user_status) => {
      console.log("Got user list update:", new_user_status);
      users = users.map((user) => {
        if (user.username === new_user_status.username) {
          return (user = new_user_status);
        } else {
          return user;
        }
      });
    });
  });
</script>

<div>
  {#each users as user}
    <p>{user.username} is active: {user.active}</p>
  {/each}
</div>
