<script>
	import { goto } from "$app/navigation";
	import axios from "axios";

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
			console.log('set to',axios.defaults.headers.common["Authorization"]);
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
