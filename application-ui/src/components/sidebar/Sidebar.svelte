<script>
    import UserInfo from "/app/src/components/sidebar/UserInfo.svelte";
    import ChatSelector from "/app/src/components/sidebar/ChatSelector.svelte";
    import PeerInfo from "/app/src/components/sidebar/PeerInfo.svelte";
    import ThroughputTests from "/app/src/components/sidebar/ThroughputTests.svelte";

    export let handleRoomSelection, selectedRoom;
</script>

<div id="sidebar">
    <UserInfo />
    <ChatSelector {handleRoomSelection} {selectedRoom} />
    <PeerInfo />
    <ThroughputTests />
</div>

<style>
    #sidebar {
        width: 340px;
        background-color: #2d2d2d;
        color: #fff;
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
        height: calc(100% - 32px);
        padding: 16px;
    }
</style>
