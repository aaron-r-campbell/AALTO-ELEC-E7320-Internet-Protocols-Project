import { writable } from 'svelte/store';

// Initial socket state
const initialState = {
    socket: null,
    token: null,
};

// Create a writable store
const state = writable(initialState);

export { state };