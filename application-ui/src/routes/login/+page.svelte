<script>
	import axios from "axios";
	import { goto } from "$app/navigation";
	import { state } from "../../stores/state_store.js";

	let username = "",
		password = "";

	const submit = async () => {
		const response = await axios.post("/api/login", { username, password });

		if (response.status === 200) {
			// Update the token
			state.set({ ...$state, token: response.data.token });

			// Set axios bearer token header for use with withCredentials
			axios.defaults.headers.common["Authorization"] =
				`Bearer ${$state.token}`;

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
