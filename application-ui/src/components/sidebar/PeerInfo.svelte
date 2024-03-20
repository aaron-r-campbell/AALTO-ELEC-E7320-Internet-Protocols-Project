<script>
  import { onMount } from "svelte";
  import { state } from "/app/src/stores/state_store.js";
  let users = [];

  onMount(() => {
    // console.log("Starting to listen for user list");

    $state.socket.on("user_activities", (new_user_activities) => {
      // console.log("Received new user list:", new_user_activities);

      users = new_user_activities.map((user) => {
        return { ...user, latency: null };
      });
    });

    $state.socket.on("user_activities_update", (new_user_status) => {
      // console.log("Got user list update:", new_user_status);
      users = users.map((user) => {
        if (user.username === new_user_status.username) {
          return { ...new_user_status, latency: null };
        } else {
          return user;
        }
      });
    });

    // console.log("Starting to listen to pings");
    // Listen for events from the socket
    $state.socket.on("ping", (timestamp) => {
      // console.log("Received ping with timestamp:", timestamp);

      $state.socket.emit("ping_ack", timestamp);
    });

    // console.log("Registering ping_result");

    $state.socket.on("ping_result", (latency, username) => {
      // console.log("Received ping_result with value:", latency);

      users = users.map((user) => {
        if (user.username === username) {
          return { ...user, latency: latency };
        } else {
          return user;
        }
      });
    });
  });
</script>

<h2>User Statuses</h2>
<div
  style="display: flex; gap: 8px; flex-wrap: wrap; overflow: hidden auto; color: var(--text-color); max-height: 400px;"
>
  {#each users as user}
    <div
      class="pill"
      style={user.latency
        ? "background-color: var(--primary-green);"
        : "background-color: #ccc;"}
    >
      {user.username}
      {#if user.latency}
        ({user.latency} ms)
      {/if}
    </div>
  {/each}
</div>

<style>
  .pill {
    border-radius: 16px;
    padding: 8px 16px;
    display: inline-flex;
    align-items: center;
    position: relative;
    height: fit-content;
  }
</style>
