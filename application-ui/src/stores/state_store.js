import { writable } from 'svelte/store';

const initialState = {
    socket: null,
    token: null,
};

const state = writable(initialState);

export { state };
