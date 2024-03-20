<script>
    export let time = new Date();
    let formattedTimestamp = "Error";

    function formatTimestamp(time) {
        const now = new Date();
        const diff = now - time;

        // If within 1 minute, show 'Just Now'
        if (diff < 60 * 1000) {
            return "Just Now";
        }

        // If from today, show 'Today'
        if (
            time.getDate() === now.getDate() &&
            time.getMonth() === now.getMonth() &&
            time.getFullYear() === now.getFullYear()
        ) {
            const options = {
                hour: "numeric",
                minute: "numeric",
                hour12: false,
            };
            return "Today " + time.toLocaleString("default", options);
        }

        // If from yesterday, show 'Yesterday'
        const yesterday = new Date(now);
        yesterday.setDate(now.getDate() - 1);
        if (
            time.getDate() === yesterday.getDate() &&
            time.getMonth() === yesterday.getMonth() &&
            time.getFullYear() === yesterday.getFullYear()
        ) {
            const options = {
                hour: "numeric",
                minute: "numeric",
                hour12: false,
            };
            return "Yesterday " + time.toLocaleString("default", options);
        }

        // Otherwise, format the date and time
        const options = {
            hour: "numeric",
            minute: "numeric",
            hour12: false,
            month: "short",
            day: "numeric",
        };

        return time.toLocaleString("default", options);
    }

    function updateTimestamp() {
        formattedTimestamp = formatTimestamp(time);
    }

    updateTimestamp();
</script>

{formattedTimestamp}
