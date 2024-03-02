<script>
    import axios from "axios";
    import { onMount } from "svelte";

    export let user;

    const get_username = async () => {
        const response = await axios.get(
            "/api/whoami",
            {},
            { withCredentials: true },
        );
        user.username = response.data.username;
    };

    onMount(async () => {
        get_username();
    });
</script>

<div id="current-user-info">
    <p>{user.username}</p>
</div>

<style>
    #current-user-info {
        text-align: center;
        padding: 10px;
        background-color: #3498db;
        color: white;
        font-weight: bold;
        margin-bottom: 20px;
    }
</style>
