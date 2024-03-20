<script>
    import UserInfo from "/app/src/components/sidebar/UserInfo.svelte";
    import ChatSelector from "/app/src/components/sidebar/ChatSelector.svelte";
    import PeerInfo from "/app/src/components/sidebar/PeerInfo.svelte";
    import ThroughputTests from "/app/src/components/sidebar/ThroughputTests.svelte";

    export let handleRoomSelection, selectedRoom;
</script>

<div id="sidebar">
    <UserInfo />
    <div style="flex-grow: 1;">
        <ChatSelector {handleRoomSelection} {selectedRoom} />
    </div>
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
        padding: 16px;
        height: 100%;
    }
</style>
