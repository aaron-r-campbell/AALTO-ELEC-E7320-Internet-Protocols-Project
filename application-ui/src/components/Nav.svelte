<script context="module">
    import ChatRoom from "./ChatRoom.svelte";
    import File from "./files/File.svelte";

    export const navOptions = [
        { page: 'messages', component : ChatRoom},
        { page: 'file', component: File }
    ];
</script>