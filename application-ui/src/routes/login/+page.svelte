<script>
	import { goto } from "$app/navigation";
	import axios from "axios";
	import io from "socket.io-client";

	let username = "",
		password = "";

	const submit = async () => {
		const response = await axios.post(
			"/api/login",
			{ username, password },
			{ withCredentials: true },
		);

		if (response.status === 200) {
			axios.defaults.headers.common["Authorization"] =
				`Bearer ${response.data.token}`;
			console.log("set to", axios.defaults.headers.common["Authorization"]);

			response.data.token;
			const socket = io("http://localhost:7777");

			socket.emit("authenticate", response.data.token);

			goto("/");
		}
	};
</script>

<form on:submit|preventDefault={submit}>
	<h1>Please sign in</h1>

	<br />

	<label for="username">Username</label>
	<input bind:value={username} type="username" placeholder="username" />

	<br />

	<label for="password">Password</label>
	<input bind:value={password} type="password" placeholder="password" />

	<br />

	<button type="submit">Submit</button>
</form>
