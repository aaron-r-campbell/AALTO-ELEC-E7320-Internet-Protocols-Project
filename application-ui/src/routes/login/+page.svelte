<script>
	import axios from "axios";
	import { goto } from "$app/navigation";
	import { state } from "/app/src/stores/state_store.js";

	let username = "",
		password = "";

	const submit = async () => {
		try {
			const response = await axios.post("/api/token", {
				username,
				password,
			});

			if (response.status === 200) {
				// Update the token
				state.set({
					...$state,
					token: response.data.token,
					username: username,
				});

				// Set axios bearer token header for use with withCredentials
				axios.defaults.headers.common["Authorization"] =
					`Bearer ${$state.token}`;

				// Logged in, go back to the main page.
				goto("/");
			} else throw Error("Invalid Login Info.");
		} catch {
			alert("Invalid login info.");
		}
	};
</script>

<div class="centerInner">
	<div class="card">
		<h1>Sign in</h1>
		<form on:submit|preventDefault={submit}>
			<label for="username">Username</label>
			<input
				class="fw"
				bind:value={username}
				type="text"
				placeholder="Enter your username"
				required
			/>

			<label for="password">Password</label>
			<input
				class="fw"
				bind:value={password}
				type="password"
				placeholder="Enter your password"
				required
			/>

			<button type="submit" class="fw">Sign in</button>
		</form>
	</div>
</div>

<style global>
	@import "/app/public/style.css";
</style>
