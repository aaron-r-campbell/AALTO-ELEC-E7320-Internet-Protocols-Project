<script>
    import Chat from "../components/Chat.svelte";
    export let data;
    const { chatId } = data;

    let username = "";

    const check_auth = async () => {
        console.log("auth is ", axios.defaults.headers.common["Authorization"]);
        if (!axios.defaults.headers.common["Authorization"]) {
            goto("/login");
            return;
        }
        const response = await axios.get(
            "/api/whoami",
            {},
            { withCredentials: true },
        );
        username = response.data.username;
    };

    onMount(async () => {
        check_auth();
    });
</script>

<h1>{chatId}</h1>
<Chat bind:current_user={username} />
