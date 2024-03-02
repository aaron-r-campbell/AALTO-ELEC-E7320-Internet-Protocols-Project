<script>
	import { goto } from "$app/navigation";
	import axios from "axios";
	import io from "socket.io-client";
	import { state } from "../../stores/state_store.js";

	let username = "",
		password = "";

	const submit = async () => {
		const response = await axios.post(
			"/api/login",
			{ username, password },
			{ withCredentials: true },
		);

		if (response.status === 200) {
			// Set axios bearer token header for use with withCredentials
			axios.defaults.headers.common["Authorization"] =
				`Bearer ${state.token}`;

			// Setup socket connection
			const socket = io("http://localhost:7777", {
				auth: { token: response.data.token },
			});

			// Update
			state.set({
				...state,
				token: response.data.token,
				socket: socket,
			});

			// Logged in, go back to the main page.
			goto("/");
		}
	};
</script>

<form on:submit|preventDefault={submit}>
	<h1>Sign in:</h1>

	<br />

	<label for="username">Username</label>
	<input bind:value={username} type="username" placeholder="username" />

	<br />

	<label for="password">Password</label>
	<input bind:value={password} type="password" placeholder="password" />

	<br />

	<button type="submit">Submit</button>
</form>
