<script>
    import axios from "axios";
    import { onMount } from "svelte";

    let friendly_name = "";

    const get_friendly_name = async () => {
        const response = await axios.get(
            "/api/whoami",
            {},
            { withCredentials: true },
        );
        friendly_name = response.data.friendly_name;
    };

    onMount(async () => {
        get_friendly_name();
    });
</script>

<div id="current-user-info">
    <p>{friendly_name}</p>
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
