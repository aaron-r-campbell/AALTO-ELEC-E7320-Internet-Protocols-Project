<script context="module">
    import ChatRoom from "./ChatRoom.svelte";
    import FileView from "./files/FileView.svelte";

    export const navOptions = [
        { page: 'messages', component : ChatRoom},
        { page: 'file', component: FileView }
    ];
</script>